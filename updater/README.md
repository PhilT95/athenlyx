# AthenlyX Updater

A small service that updates the website **by itself**. When GitHub tells it
that a new version is on `main`, it fetches the code, builds new Docker images,
swaps the running containers and rolls back if the new version does not start.

It replaces the old `scripts/sync.sh` deployment script.

- [Overview](#overview)
- [Files](#files)
- [Architecture and security model](#architecture-and-security-model)
- [Configuration](#configuration)
- [HTTP API](#http-api)
- [Authentication](#authentication)
- [How the code works](#how-the-code-works)
- [The update procedure](#the-update-procedure)
- [Concurrency](#concurrency)
- [State and persistence](#state-and-persistence)
- [Failure handling](#failure-handling)
- [Operations](#operations)
- [Testing](#testing)
- [Limitations and design decisions](#limitations-and-design-decisions)

---

## Overview

```
GitHub (merge to main)
   │  POST /hooks/update   (signed with HMAC)
   ▼
host nginx ──▶ updater container
                  1. verify the signature
                  2. start the update in a background thread, answer 202
                  3. git fetch main  → build images → docker compose up --wait
                     └─ unhealthy? → roll back to the previous version
```

Key properties:

- **No registry.** Images are built on the server from the Git repository and
  stay local. No dependency on GHCR or Docker Hub.
- **The request cannot choose what is deployed.** The updater always builds
  the newest commit of one configured branch from one configured repository.
- **A failed build never affects the running site.** The new version is built
  next to the old one, and containers are replaced only after the build succeeded.
- **Idempotent.** Repeated or replayed requests redeploy nothing if the newest commit is already running.

## Files

| File | Purpose |
|---|---|
| `main.py` | FastAPI app. Defines the three endpoints and wires authentication to the runner. |
| `auth.py` | Request signature verification (`sign()`, `Verifier`) and replay protection. |
| `config.py` | `Config` dataclass: reads and validates environment variables. |
| `runner.py` | `Runner`: scheduling, the update procedure, rollback, state persistence. |
| `Dockerfile` | Image with Python, `git`, the `docker` CLI and the Compose plugin. |
| `requirements.txt` | Runtime dependencies (`fastapi`, `uvicorn`, `docker`). |
| `requirements-dev.txt` | Adds `pytest` and `httpx` for the tests. |
| `tests/` | Automated tests (`conftest.py`, `test_auth.py`, `test_api.py`, `test_runner.py`). |

Related files outside this directory:

- `compose.yaml`: the `updater` and `docker-proxy` services.
- `.env.example`: the settings.
- `scripts/update-request.sh`: sends one signed request (manual trigger or status check).
- `scripts/wait-for-update.sh`: waits until an update has finished and reports the result.
- `.github/workflows/deploy.yml`: the GitHub workflow that triggers the updater after a merge.
  See [`.github/workflows/README.md`](../.github/workflows/README.md).

## Architecture and security model

Four containers are involved (see `compose.yaml`):

| Service | Role |
|---|---|
| `web` | nginx for the static site (updated by the updater). |
| `api` | Content API (updated by the updater). |
| `updater` | This service. Not updated by itself. |
| `docker-proxy` | Filters the Docker API. Only the updater can reach it. |

### Why a socket proxy

To build images and replace containers, the updater must talk to the Docker
daemon. Access to the Docker socket (`/var/run/docker.sock`) is equivalent to
root on the host. The updater therefore gets no socket. It sets
`DOCKER_HOST=tcp://docker-proxy:2375` and talks to `tecnativa/docker-socket-proxy`,
which allows only these API sections: `CONTAINERS`, `IMAGES`, `NETWORKS`, `BUILD`,
`INFO`, `POST`. All other sections (volumes, secrets, swarm, exec and others)
are blocked. The `docker-api` network between them is `internal` (no internet
access, no published ports).

> **Be aware of the limit:** the proxy filters by API section, not by intent.
> Because `CONTAINERS` and `POST` are enabled, a compromised updater could still
> create containers. The signature check is the real protection, and the
> updater's behavior is fixed (see below). Keep `UPDATE_SECRET` secret and do
> not expose the updater port beyond the host nginx.

### Trust model

| Risk | Mitigation |
|---|---|
| A stranger calls the endpoint | HMAC-SHA256 signature required (see [Authentication](#authentication)). |
| A captured request is sent again later | Timestamp window of 5 minutes, and each signature is accepted once. |
| An attacker tries to make the server build arbitrary code | The payload is ignored for the source. Only `REPO_URL` at `ALLOWED_REF` is ever built. |
| Bad code reaches `main` | Not the updater's job. Use branch protection so that only merged, checked code reaches `main`. |
| Build breaks the live site | New images are built first. Containers are replaced only after a successful build, and rolled back if unhealthy. |
| Container compromise | Non-root user, read-only root filesystem, `no-new-privileges`. |

## Configuration

All settings are environment variables, set in `compose.yaml` from your `.env` file.
`config.py` reads them once at startup. **The service refuses to start** if
`REPO_URL` is missing or `UPDATE_SECRET` is shorter than 32 characters.

| Variable | Default | Meaning |
|---|---|---|
| `REPO_URL` | (required) | Git URL to fetch from. The only repository the updater will ever build. |
| `UPDATE_SECRET` | (required, min. 32 chars) | Shared secret for request signatures. Generate with `openssl rand -hex 32`. |
| `ALLOWED_REF` | `refs/heads/main` | The branch that gets deployed. |
| `KEEP_IMAGES` | `3` | Number of old image versions kept per service. |
| `UPDATER_PORT` | `6560` | Host port (bound to `127.0.0.1`) the updater is published on. Used in `compose.yaml` only. |
| `DOCKER_HOST` | set in `compose.yaml` | Address of the Docker API (the socket proxy). |

Settings that exist in `config.py` but have no entry in `compose.yaml` (they
use their defaults; add them to the `environment:` block to change them):

| Variable | Default | Meaning |
|---|---|---|
| `COMPOSE_FILE` | `/deploy/compose.yaml` | Compose file used to replace the containers. |
| `COMPOSE_PROJECT` | `athenlyx` | Compose project name. Also the prefix of image names (`athenlyx-api`, `athenlyx-web`). It must match `name:` and the `image:` names in `compose.yaml`. |
| `STATE_DIR` | `/state` | Where `state.json` is stored (a Docker volume). |
| `WORK_DIR` | `/work` | Scratch space for source checkouts (a tmpfs). |
| `HEALTH_TIMEOUT` | `180` | Seconds to wait for the new containers to become healthy. |
| `BUILD_TIMEOUT` | `1800` | Timeout for the connection to the Docker daemon while building. |

The services that are updated (`api`, `web`) are fixed in `config.py`
(`Config.services`). Each name is both a Compose service and a Dockerfile target.

## HTTP API

The updater listens on port 8000 inside its container. The `/docs` and
`/openapi.json` pages are disabled.

| Method and path | Auth | Purpose |
|---|---|---|
| `POST /hooks/update` | yes | Start an update. |
| `GET /hooks/update/status` | yes | Show what is running and what happened last. |
| `GET /hooks/health` | no | Liveness check (used by the Docker `HEALTHCHECK`). |

### `POST /hooks/update`

Body: empty, or a JSON object. If it contains a `"ref"` that differs from
`ALLOWED_REF`, the request is answered with `ignored` and nothing is built.
All other fields in the body are ignored. They cannot influence what is deployed.

```json
{ "ref": "refs/heads/main" }
```

| Status | Body | Meaning |
|---|---|---|
| `202` | `{"status": "started"}` | An update was started in the background. |
| `202` | `{"status": "queued"}` | An update is already running. Another run follows when it ends. |
| `202` | `{"status": "ignored", "reason": "..."}` | The `ref` is a different branch. Nothing happens. |
| `400` | | Body is not valid JSON. |
| `401` | `{"detail": "Unauthorized."}` | Signature, timestamp or replay check failed. The reason is only in the server log. |

`202` means "accepted", not "finished". Use the status endpoint to follow the result.

### `GET /hooks/update/status`

```json
{
  "running": false,
  "pending": false,
  "current_sha": "8512d6e3a1bc...",
  "current_tag": "8512d6e3a1bc",
  "previous_tag": "0e6b60c56517",
  "last_result": {
    "outcome": "success",
    "sha": "8512d6e3a1bc...",
    "started": "2026-10-08T22:10:01+00:00",
    "finished": "2026-10-08T22:11:20+00:00"
  },
  "log": ["2026-10-08T22:10:01+00:00 Fetching refs/heads/main from ..."]
}
```

`last_result.outcome` is `success`, `up-to-date` or `failed` (with an `error`
text and `sha: null`). `log` shows the last 30 messages.

## Authentication

Every request to `/hooks/update` and `/hooks/update/status` must carry two headers:

```
X-Timestamp: <unix time in seconds>
X-Signature: sha256=<hex HMAC-SHA256>
```

The signature is calculated over the timestamp, a dot and the **raw request
body** (empty for `GET`), using `UPDATE_SECRET` as the key:

```
signature = "sha256=" + hex( HMAC_SHA256( key = UPDATE_SECRET, message = timestamp + "." + body ) )
```

Example with `openssl` (the same thing `scripts/update-request.sh` does):

```bash
ts=$(date +%s)
body='{"ref":"refs/heads/main"}'
sig="sha256=$(printf '%s.%s' "$ts" "$body" | openssl dgst -sha256 -hmac "$UPDATE_SECRET" -hex | sed 's/^.* //')"
curl -X POST http://127.0.0.1:6560/hooks/update \
  -H "X-Timestamp: $ts" -H "X-Signature: $sig" \
  -H "Content-Type: application/json" -d "$body"
```

The body used for signing must be **byte-identical** to the body sent.

### Checks performed (`auth.Verifier.verify`)

In this order. Any failure raises `AuthError`, which `main.py` turns into `401`:

1. Both headers are present.
2. The timestamp is an integer.
3. `|now - timestamp| <= 300` seconds (`Config.max_clock_skew`). This also
   needs the clocks of GitHub and your server to be roughly in sync.
4. The signature matches the expected one. It is compared with
   `hmac.compare_digest`, which takes the same time for any input and therefore does not leak how many characters were right.
5. The signature has not been used before within the window (replay protection).
   Used signatures are kept in memory in a dict and dropped once they are older than the window.

Replay protection is in memory only, so it resets when the container restarts.
That is acceptable because the timestamp window is short and updates are
idempotent.

The `401` response never says which check failed. The reason is logged
(`Rejected request from <ip>: <reason>`).

## How the code works

### `main.py`

Creates the objects once at import time:

```python
cfg      = Config.from_env()                          # fails fast on bad config
verifier = Verifier(cfg.update_secret, cfg.max_clock_skew)
runner   = Runner(cfg)
```

`_authenticate()` reads the raw body, calls `verifier.verify()` and maps
`AuthError` to `HTTP 401`. It returns the body so the endpoint can use it.

- **`update()`** authenticates, parses the optional JSON body, ignores other
  refs, then calls `runner.trigger()` and returns its result (`started` or `queued`).
- **`update_status()`** authenticates and returns `runner.status()`.
- **`health()`** returns `{"status": "ok"}`.

The endpoints do no work themselves. They only authenticate and delegate.

### `auth.py`

- `sign(secret, timestamp, body)` computes the signature string. It is used by
  the verifier and by the tests.
- `Verifier` holds the secret, the allowed clock skew and the dict of recently
  seen signatures (guarded by a `Lock`).

### `config.py`

`Config` is a frozen dataclass (its values cannot change after creation).
`Config.from_env()` reads environment variables, converts numbers, applies
defaults and raises `RuntimeError` for missing or weak required values.

### `runner.py`

The class is organized in four parts. See the next sections for details.

| Part | Methods |
|---|---|
| Scheduling | `trigger()`, `_loop()`, `running` |
| The update | `run_once()` |
| Steps | `_fetch()`, `_build()`, `_compose_up()`, `_prune()` |
| Helpers | `_run()`, `_say()`, `_record()`, `_load_state()`, `_save_state()`, `status()` |

Each step is a small method so tests can replace it with a fake. The decision
logic in `run_once()` can then be tested without Docker or network access.

## The update procedure

`Runner.run_once()` performs one complete update:

```
 1. create a fresh temp directory under WORK_DIR
 2. _fetch()        git fetch ALLOWED_REF from REPO_URL, return the commit SHA
 3. same SHA as state.current_sha?  → record "up-to-date", stop
 4. _build()        build athenlyx-api:<tag> and athenlyx-web:<tag>   (tag = first 12 chars of SHA)
 5. remember previous = state.current_tag
 6. _compose_up(tag)
        failure → _compose_up(previous) if there is one → report "failed"
 7. state: previous_tag = previous, current_tag = tag, current_sha = sha
 8. record "success", _prune() old images
 9. (always) delete the temp directory
```

Any exception is caught at the end, logged and recorded as `failed`. It never
escapes the thread.

### `_fetch()`

```
git init -q <dir>
git -C <dir> remote add origin <REPO_URL>
git -C <dir> fetch -q --no-tags origin <ALLOWED_REF>
git -C <dir> rev-parse FETCH_HEAD          → the SHA
git -C <dir> checkout -q --detach FETCH_HEAD
```

The history is fetched in full (no `--depth`) and `origin` is set because the
SEO plugin used during the site build reads page creation dates, modification
dates and authors from git history, and the repository URL from `origin`.
`GIT_TERMINAL_PROMPT=0` makes git fail instead of waiting for a password.

### `_build()`

Uses the Docker SDK for Python (`client.api.build`) with the checkout as the
build context, once per service in `Config.services`:

| Argument | Value |
|---|---|
| `path` | The temp checkout |
| `tag` | `<project>-<service>:<tag>`, for example `athenlyx-web:8512d6e3a1bc` |
| `target` | The service name, selecting the matching stage of the root `Dockerfile` |

The call returns a stream of JSON messages. A message with an `error` key
raises `UpdateError`. Lines starting with `Step ` are copied into the log.

The SDK uses Docker's classic build endpoint instead of BuildKit. BuildKit needs
extra API sections through the socket proxy. Because of this, the root
`Dockerfile` must not use BuildKit-only features (it has no `# syntax=` line
for that reason).

### `_compose_up(tag)`

Runs, with the environment variable `IMAGE_TAG=<tag>`:

```
docker compose -p <project> -f /deploy/compose.yaml --project-directory /deploy \
  up -d --no-build --no-deps --pull never --wait --wait-timeout <HEALTH_TIMEOUT>  api web
```

| Flag | Reason |
|---|---|
| `-p <project>` | Same Compose project as a manual `docker compose up`, so the existing containers are replaced instead of duplicated. |
| `--no-build`, `--pull never` | Images were already built locally. Never build here and never contact a registry. |
| `--no-deps` | Only the listed services are touched. |
| `--wait` | Return only when the containers are **healthy** (uses the Dockerfile `HEALTHCHECK`s). On timeout the command fails. |
| `api web` | Only these. The updater never restarts itself or the proxy. |

`compose.yaml` contains `image: athenlyx-web:${IMAGE_TAG:-local}`. Compose
treats a different tag as a different image and recreates the container. An
environment variable overrides the value in `.env`.

Rolling back is the same command with the previous tag.

### `_prune()`

For each service it lists the local images of that repository, newest first,
and removes those beyond the newest `KEEP_IMAGES`, **except** the current and
previous tags. All errors are caught. A failed cleanup never fails an update.

### `_run()`

Runs an external command with a timeout and captured output. A non-zero exit
code or a timeout raises `UpdateError` with the last five lines of output.

## Concurrency

Only one update runs at a time. This is controlled by `trigger()` and `_loop()`:

```python
def trigger(self):
    with self._mu:                 # lock: one thread changes the flags at a time
        if self._running:
            self._pending = True   # remember that another run is wanted
            return "queued"
        self._running = True
    threading.Thread(target=self._loop, daemon=True).start()
    return "started"

def _loop(self):
    while True:
        try:    self.run_once()
        except Exception: log.exception(...)
        with self._mu:
            if self._pending:
                self._pending = False
                continue           # run once more
            self._running = False
            return
```

- The update runs in a background thread so that the HTTP request can answer
  immediately (a build takes minutes).
- A request that arrives during a run only sets `_pending`. Any number of such
  requests lead to **one** extra run, which is enough because every run builds
  the newest commit.
- `_pending` is cleared while holding the lock, so a request arriving at that
  moment is not lost.
- The `try/except` around `run_once()` ensures `_running` is always reset.

Example:

```
t=0   request A → started   (run 1 begins)
t=20  request B → queued
t=40  request C → queued    (no additional effect)
t=90  run 1 ends, pending was set → run 2 begins (newest commit)
t=150 run 2 ends, nothing pending → thread ends
```

## State and persistence

`State` (a dataclass) is stored in `STATE_DIR/state.json` (the `updater-state`
Docker volume):

| Field | Meaning |
|---|---|
| `current_sha` | Full commit SHA of the running version. Used to detect "nothing to do". |
| `current_tag` | The 12-character image tag of the running version. |
| `previous_tag` | The version before. Used for rollback and protected from pruning. |
| `last_result` | `{outcome, sha, started, finished[, error]}` of the last run. |

- The state is written after each run (`_record` → `_save_state`).
- Writing is **atomic**: the content goes to `state.tmp` and is then renamed
  to `state.json`, so a crash cannot leave a half-written file.
- If the file is missing or unreadable, an empty state is used. The next
  trigger then performs a full deploy.
- `current_*` values are only changed **after** the new version is healthy,
  so the state always describes what is actually running.

The log shown by the status endpoint is a ring buffer of the last 200 messages
in memory (`collections.deque(maxlen=200)`). It is lost on restart. The same
messages also go to the container log (`docker logs`).

## Failure handling

| Failure | What happens | Site state |
|---|---|---|
| `REPO_URL` unreachable or the branch does not exist | `_fetch` raises. Recorded as `failed`. | Unchanged |
| Site build fails (for example `zensical build --strict` finds an error) | `_build` raises. Recorded as `failed`. | Unchanged |
| New containers do not become healthy within `HEALTH_TIMEOUT` | `_compose_up` raises. The previous tag is started again. Recorded as `failed`. | Previous version |
| Rollback also fails | Logged as `Rollback failed too`. Recorded as `failed`. | Needs manual attention |
| No previous version (first deploy) and start fails | Recorded as `failed`. No rollback possible. | Whatever Compose left. Check `docker compose ps`. |
| Image cleanup fails | Logged. The update still counts as successful. | New version |
| Updater container restarts during an update | The run is lost. State on disk still shows the last completed version. Trigger again. | Depends on the point of interruption |

## Operations

### First start

```bash
cp .env.example .env
# set UPDATE_SECRET (openssl rand -hex 32), REPO_URL, ports
docker compose up -d --build
```

The first start builds the images from your working copy (tag `local`). The
state is empty, so the first update request deploys the newest commit of `ALLOWED_REF`.

### Trigger and inspect

```bash
UPDATE_SECRET=... scripts/update-request.sh update    # POST /hooks/update
UPDATE_SECRET=... scripts/update-request.sh status    # GET  /hooks/update/status
docker logs -f athenlyx-updater-1                     # live log of the update
```

The script uses `http://127.0.0.1:6560` by default. A different base URL can be passed as the second argument.

### Behind the host nginx

The updater is published on `127.0.0.1:${UPDATER_PORT}` only. Route `/hooks/`
to it in the host nginx, and make sure your WAF does not block or challenge it:

```nginx
location /hooks/ {
    proxy_pass         http://127.0.0.1:6560;
    proxy_http_version 1.1;
    proxy_set_header   Host              $host;
    proxy_set_header   X-Real-IP         $remote_addr;
    proxy_set_header   X-Forwarded-For   $proxy_add_x_forwarded_for;
    proxy_set_header   X-Forwarded-Proto $scheme;
}
```

### Updating the updater itself

The updater never replaces itself. After changing code in `updater/`:

```bash
docker compose up -d --build updater
```

### Testing a branch other than `main`

Set `ALLOWED_REF=refs/heads/<branch>` in `.env`, recreate the updater
(`docker compose up -d updater`), and trigger an update. Remember to change it
back. Requests with a `ref` different from `ALLOWED_REF` are ignored.

### Rolling back by hand

Previous images are kept. To switch to one:

```bash
docker images | grep athenlyx
IMAGE_TAG=<tag> docker compose up -d --no-build api web
```

The updater's recorded state is then out of sync until its next successful update.

## Testing

```bash
cd updater
pip install -r requirements-dev.txt
python -m pytest -q
```

33 tests. None need Docker or internet access. The script tests need `bash`,
`curl`, `openssl` and `jq`, and are skipped if one is missing:

| File | Covers |
|---|---|
| `tests/test_auth.py` | Valid signature; missing headers; wrong secret; changed body; old or future timestamp; non-numeric timestamp; replay. |
| `tests/test_api.py` | Public health endpoint; `401` without or with a wrong signature; successful trigger; other branch ignored; invalid JSON; payload cannot select the source; status endpoint. Uses FastAPI's `TestClient` and replaces `runner.trigger`. |
| `tests/test_scripts.py` | `scripts/update-request.sh` and `scripts/wait-for-update.sh` against a real in-process updater server: signed request accepted, wrong secret rejected, status request, wait script returns success / up-to-date / failure / timeout, ignores results older than the trigger, keeps waiting while an update is running. |
| `tests/test_runner.py` | First deploy; same SHA is a no-op; update keeps the previous tag; failed start rolls back; failed build leaves the old version; state survives a restart; concurrent triggers are coalesced. The Docker steps are replaced by fakes. |

**Not covered by tests:** the real `_build()`, `_compose_up()` and `_prune()`
(they need a Docker daemon). `_fetch()` was checked manually against a local
repository. A real end-to-end run on the server is the verification for these.

## Limitations and design decisions

- **Classic builder (deprecated by Docker).** `_build()` uses the Docker SDK for Python, which talks to the engine's classic build endpoint. Docker has deprecated this builder ("will be removed in a future release"). It still works in Docker Engine 29.x. The `Docker Check` workflow builds with the classic builder so a future incompatibility is found in CI. If it is removed, `_build()` must switch to BuildKit (`docker buildx build`). This needs the `SESSION` and `GRPC` sections to be allowed in `docker-proxy`, and a builder that works over a TCP endpoint. Keep the `Dockerfile` free of BuildKit-only features until then.
- **Builds happen on the server.** CPU and memory are used while a build runs. The live site keeps serving, but a very small server can slow down.
- **Full history fetch.** Needed for the SEO plugin's page dates. It is small for this repository but grows with it.
- **Not self-updating.** Deliberate, to avoid an updater that kills itself half-way. Update it by hand.
- **In-memory replay protection and log.** Both reset on restart.
- **No built-in rate limiting.** Apply it in the host nginx or the WAF.
- **Tied to the Compose setup.** The services, image names and `IMAGE_TAG` mechanism must match `compose.yaml` (see `COMPOSE_PROJECT` above).
- **Compose file is read from the server.** `/deploy/compose.yaml` is mounted from the server's copy of `compose.yaml`. Changes to `compose.yaml` in Git are **not** picked up automatically. Copy it to the server and recreate the affected services by hand.
- **Same applies to `.env`.** Settings are read from the server's `.env`.
