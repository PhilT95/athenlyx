# Zensical in Docker with automatic updates

This guide shows how to run a Zensical website in Docker and update it automatically after every merge to `main`. It describes the setup that runs this website. It replaces the older approach of a cron job that pulls from Git and copies files into a web directory.

After the setup, publishing is a single step: merge a pull request. GitHub notifies a small service on your server, which builds the new version, switches over and rolls back if the new version does not start.

## How it works

```
Pull request ──▶ checks pass ──▶ merge to main
                                      │
                       GitHub workflow sends a signed request
                                      ▼
Host nginx ──▶ updater ──▶ fetches main ──▶ builds images ──▶ replaces containers
                                                                  │
                                              unhealthy? ──▶ rollback to the old version
```

The server builds the images itself from your Git repository. No container registry is involved, so you do not depend on a specific hosting provider.

### The containers

| Container | Purpose |
|---|---|
| `web` | nginx that serves the static site and forwards `/api/` to the API |
| `api` | A small FastAPI service for search and page content as JSON |
| `updater` | Receives the update request and rebuilds `web` and `api` |
| `docker-proxy` | Limits what the updater is allowed to ask the Docker engine |

Only `web` and `updater` publish a port, and both bind to `127.0.0.1`. Your existing nginx on the host stays in front and handles TLS.

## Requirements

- [x] A Linux server with
    - [X] Docker Engine and the Docker Compose plugin
    - [X] nginx on the host, already serving your domain over HTTPS
    - [X] A user that is allowed to run `docker` commands
- [x] A Zensical project in a Git repository on GitHub
- [x] Permission to change the repository settings on GitHub

!!! note
    The classic Docker builder is deprecated but still works in Docker Engine 29. The updater uses it, because the newer BuildKit builder needs more access to the Docker engine than the proxy allows. See the [updater documentation](https://github.com/PhilT95/athenlyx/blob/main/updater/README.md) for the details.

## Files in the repository

| File | Purpose |
|---|---|
| `Dockerfile` | Builds the site and defines the `api` and `web` images |
| `docker/nginx.conf` | nginx configuration inside the `web` container |
| `compose.yaml` | Defines the four containers |
| `.env.example` | Template for your settings |
| `updater/` | The updater service |
| `api/` | The content API |
| `scripts/` | Helper scripts for manual update requests |
| `.github/workflows/deploy.yml` | Sends the update request after a merge |

You can copy these files into your own repository. To adapt them, change the domain in `zensical.toml` and in `scripts/ultralytics.py`.

## Setup

### Get the files onto the server

```bash
git clone https://github.com/<user>/<repository>.git /opt/athenlyx
cd /opt/athenlyx
cp .env.example .env
chmod 600 .env
```

### Configure the settings

Open `.env` and set at least these values:

```bash
# Local ports, reachable from the server only
APP_PORT=6559
UPDATER_PORT=6560

# The repository the updater builds from, and the branch it deploys
REPO_URL=https://github.com/<user>/<repository>.git
ALLOWED_REF=refs/heads/main

# Shared secret for the signed update request (at least 32 characters)
UPDATE_SECRET=<output of: openssl rand -hex 32>
```

!!! warning "Keep the secret private"
    Anyone who knows `UPDATE_SECRET` can trigger an update. The updater only ever builds the newest commit of `ALLOWED_REF` from `REPO_URL`, so a leaked secret cannot make it build other code. Replace the secret anyway if it leaks.

### Start the containers

```bash
docker compose up -d --build
docker compose ps
```

The first start builds all images from the files on the server. All containers should report `healthy` or `running` after a short time. Test the site locally:

```bash
curl -I http://127.0.0.1:6559/
curl 'http://127.0.0.1:6559/api/v1/search?q=docker&limit=1'
```

### Point the host nginx to the containers

Add two proxy rules to the server block of your site. `/hooks/` goes to the updater and everything else goes to the site:

```nginx
location /hooks/ {
    proxy_pass         http://127.0.0.1:6560;
    proxy_http_version 1.1;
    proxy_set_header   Host              $host;
    proxy_set_header   X-Forwarded-For   $proxy_add_x_forwarded_for;
    proxy_set_header   X-Forwarded-Proto $scheme;
}

location / {
    proxy_pass         http://127.0.0.1:6559;
    proxy_http_version 1.1;
    proxy_set_header   Host              $host;
    proxy_set_header   X-Forwarded-For   $proxy_add_x_forwarded_for;
    proxy_set_header   X-Forwarded-Proto $scheme;
}
```

The repository contains a complete example in `deploy/nginx-host.conf`. Reload nginx afterwards:

```bash
nginx -t && systemctl reload nginx
```

!!! info "Using a web application firewall"
    If a firewall such as SafeLine sits in front of nginx, allow `POST` and `GET` requests to `/hooks/*`. GitHub runners use changing IP addresses, so do not rely on an IP allow list. The signature protects the endpoint.

### Configure GitHub

You need two settings. They are repository settings, so they cannot be part of the files.

**1. Environment and secret.** Go to **Settings → Environments** and create an environment named `production`. Restrict it to the `main` branch. Add a secret named `UPDATE_SECRET` with the same value as in the server's `.env` file. The workflow calls `https://athenlyx.com` by default. For your own domain, add a variable named `UPDATE_BASE_URL` with the address of your site.

**2. Protect `main`.** Under **Settings → Branches**, protect `main`:

- Require a pull request before merging.
- Require the status checks to pass: `validate`, `vale`, `secrets`, `preflight`, `images` and `updater-tests`. A check only appears in the list after it ran once, so open a pull request first.
- Do not allow bypassing the rules.

This is what makes a merge mean that the checks passed. The deploy workflow only runs on `main`, so nothing unchecked is deployed.

## Testing an update

Trigger an update by hand before you rely on the workflow:

```bash
export UPDATE_SECRET=<your secret>
scripts/update-request.sh update
docker logs -f athenlyx-updater-1
scripts/update-request.sh status
```

The log shows each step: fetch, build, start and `Now running <version>`. A second request without new commits reports `up-to-date` and changes nothing.

To try a branch other than `main`, set `ALLOWED_REF` in `.env`, recreate the updater with `docker compose up -d updater`, push the branch and run `UPDATE_REF=refs/heads/<branch> scripts/update-request.sh update`. Docker Compose reads `.env` only when it creates a container, so the recreate step is required.

## What happens during an update

1. The updater fetches the newest commit of the configured branch. If that commit is already running, it stops.
2. It builds new `api` and `web` images, tagged with the commit hash. The running site keeps serving during the build.
3. It starts the new containers and waits until their health checks pass.
4. If the new containers do not become healthy, it starts the previous version again and reports the failure.
5. It removes old images and keeps the newest three.

If the build fails, for example because of a broken link that `zensical build --strict` finds, nothing is replaced. The old script copied files over the live site, so a failed build could leave a half-updated site. That cannot happen with this setup.

Merges that arrive in quick succession are combined. The updater runs once more after the current update, and that run picks up the newest commit.

## Security notes

- The update request is signed with HMAC-SHA256. A request older than five minutes or a repeated request is rejected.
- The request cannot select what gets built. The updater builds the branch and repository from its own settings.
- The updater has no access to the Docker socket. It talks to `docker-proxy`, which allows only the Docker API sections that the update needs. The proxy still allows creating containers, so keep the secret private and do not publish the updater port beyond the host.
- All containers run with `no-new-privileges`. The `api` container has a read-only filesystem.

## Maintenance

| Task | How |
|---|---|
| Change `compose.yaml` or `.env` | Edit the files on the server, or run `git pull` in `/opt/athenlyx`, then run `docker compose up -d`. The updater does not copy these files from Git. |
| Update the updater itself | `docker compose up -d --build updater`. It does not replace itself. |
| Redeploy without a new commit | Run the **Deploy** workflow manually in GitHub Actions. |
| Roll back by hand | `IMAGE_TAG=<old tag> docker compose up -d --no-build api web`. Use `docker images` to list the old tags. |
| Change the secret | Change it in `.env` and in GitHub, then run `docker compose up -d updater`. Requests fail until both match. |

## Troubleshooting

| Symptom | Likely cause |
|---|---|
| The workflow fails with `401` | The secrets differ, or the server clock is more than five minutes off. The updater log names the reason. |
| `403` or an HTML page instead of JSON | nginx or the firewall blocks the request. Allow `/hooks/*`. |
| The response says `ignored` | The request names a different branch than `ALLOWED_REF`. |
| `Cannot locate specified Dockerfile` | The branch has no `Dockerfile`. This happens when `ALLOWED_REF` points to a branch from before the migration. |
| An update takes long | The first build downloads base images. Later builds reuse the Docker cache. |
| The status shows `failed` | The log in the status output or `docker logs athenlyx-updater-1` shows the failing step. The previous version keeps running. |

## More details

The repository contains technical documentation for each part:

- [`updater/README.md`](https://github.com/PhilT95/athenlyx/blob/main/updater/README.md) describes the update service in detail.
- [`api/README.md`](https://github.com/PhilT95/athenlyx/blob/main/api/README.md) describes the content API.
- [`.github/workflows/README.md`](https://github.com/PhilT95/athenlyx/blob/main/.github/workflows/README.md) describes the pipeline and the GitHub settings.
