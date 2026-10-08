# CI/CD workflows

This directory contains the GitHub Actions workflows of the repository and
this document, which explains how they work together to **check changes and
deploy the website automatically after a merge**.

- [Overview](#overview)
- [The deployment flow](#the-deployment-flow)
- [Workflows](#workflows)
- [Deploy workflow in detail](#deploy-workflow-in-detail)
- [One-time setup](#one-time-setup)
- [Helper scripts](#helper-scripts)
- [Operating the pipeline](#operating-the-pipeline)
- [Troubleshooting](#troubleshooting)
- [Design decisions and limitations](#design-decisions-and-limitations)

---

## Overview

| Goal | How it is achieved |
|---|---|
| Nothing reaches production unless the checks pass | **Branch protection** on `main`: changes must come through a pull request and all required checks must be green. |
| A merge deploys the site without manual steps | The **Deploy** workflow runs on every push to `main` and asks the [updater](../../updater/README.md) on the server to update. |
| A failed deployment is visible | The Deploy workflow **waits for the result** and fails if the update failed. |
| No dependency on a container registry | The server builds the images itself from the Git repository. The workflows never build or push production images. |

Only the Deploy workflow talks to the server. Every other workflow only checks the content.

## The deployment flow

```
 feature branch / docs branch
        │  open pull request
        ▼
 ┌───────────────────────────── required checks ─────────────────────────────┐
 │ Build Check · Vale Linter · Security Check · Pre-Flight · Docker Check    │
 └───────────────────────────────────────────────────────────────────────────┘
        │  all green → merge button becomes available
        ▼
 push to main (the merge commit)
        │
        ▼
 Deploy workflow ──signed POST /hooks/update──▶ updater (on the server)
        │                                          fetch main → build → replace containers
        └──signed GET /hooks/update/status (polling)◀── result: success / up-to-date / failed
```

A push to `main` can only happen through a merge that passed all checks
(branch protection). The Deploy workflow therefore does not need to check them
again.

## Workflows

| File | Name (in the Actions tab) | Job (= check name) | Trigger | Purpose |
|---|---|---|---|---|
| `build.yml` | Build Check | `validate` | push, pull request | `zensical build --strict` must succeed (no broken links or warnings). |
| `vale.yml` | Vale Linter | `vale` | push, pull request | Prose linting of `docs/` (errors fail the check). |
| `security.yml` | Security Check | `secrets` | push, pull request | Gitleaks scans for committed secrets. |
| `preflight.yml` | Pre-Flight Check | `preflight` | pull request | Changed docs need a changelog entry. New docs need a nav entry in `zensical.toml`. |
| `docker.yml` | Docker Check | `images`, `updater-tests` | push, pull request | Images build and start; updater tests pass. |
| `deploy.yml` | Deploy | `deploy` | push to `main`, manual | Triggers the update on the server and waits for the result. |

**Check names:** branch protection refers to checks by their **job name** (the
third column), not by the workflow name. The jobs have no `name:` field, so the
job ID is the name. If you rename a job, update the branch protection too.

### `docker.yml` in detail

The `images` job:

1. Checks out the full history (`fetch-depth: 0`). The site build needs it for page dates.
2. Builds the `api` and `web` targets of the root `Dockerfile` with
   `DOCKER_BUILDKIT=0`. The updater builds through the Docker API, which uses
   the classic builder, so this tests the same code path as production.
3. Starts the `api` image and checks `/api/v1/health` and that a search returns a result.
4. Starts the `web` image and checks that `index.html` is served and an unknown page gives `404`.
5. Prints the container logs if something failed.

The `updater-tests` job installs `updater/requirements-dev.txt` and runs
`pytest`. These tests include end-to-end tests of the two helper scripts
against a real instance of the updater application.

> **Why this check exists:** the updater builds the image on the server. If the
> `Dockerfile` is broken, the updater would fail and roll back (the site stays
> up), but you would find out only after merging. This check finds it before.

## Deploy workflow in detail

`deploy.yml`

```yaml
on:
  push:
    branches: [main]
  workflow_dispatch:
concurrency:
  group: deploy
  cancel-in-progress: false
```

- **Triggers:** every push to `main`, and a manual run from the Actions tab
  (useful to redeploy). The job has `if: github.ref == 'refs/heads/main'`, so a
  manual run on another branch does nothing.
- **Concurrency:** only one deployment run at a time. If several pushes arrive
  while one runs, only the newest waits. The older waiting runs are cancelled.
  That is fine, because the updater always deploys the **newest** commit of
  `main`, regardless of which run triggered it.

```yaml
environment: production
env:
  UPDATE_SECRET:   ${{ secrets.UPDATE_SECRET }}
  UPDATE_BASE_URL: ${{ vars.UPDATE_BASE_URL || 'https://athenlyx.com' }}
```

- `environment: production` makes the secret an **environment secret**. It can
  be restricted so that only workflows on `main` can read it (see [setup](#one-time-setup)).
- `UPDATE_BASE_URL` is a repository or environment **variable** (not secret). It defaults to `https://athenlyx.com`.

### Step 1: Trigger update

```bash
echo "SINCE=$(date +%s)" >> "$GITHUB_ENV"
for attempt in 1 2 3; do
  scripts/update-request.sh update "$UPDATE_BASE_URL" && exit 0
  sleep 10
done
exit 1
```

- `SINCE` records the time just **before** the request. The next step only
  accepts an update result that finished **at or after** this time. Without it,
  the workflow could report the result of an earlier update.
- Up to three attempts, because the server or the network may be briefly
  unavailable. Each attempt is signed again with a new timestamp. A signature
  can be used only once, so resending the same request would be rejected as a replay.
- The updater answers `202` (`started` or `queued`). The script fails on any HTTP error.

### Step 2: Wait for the update to finish

`scripts/wait-for-update.sh "$UPDATE_BASE_URL" "$SINCE" 1200`

Polls the updater's status endpoint every 15 seconds for up to 20 minutes. It
reports a result only when **all** of these are true:

1. `running` is `false`.
2. `pending` is `false` (no queued follow-up run).
3. `last_result.finished` is at or after `SINCE`.

Then it prints the updater log and exits:

| `last_result.outcome` | Exit code | Meaning |
|---|---|---|
| `success` | 0 | The new version is running. |
| `up-to-date` | 0 | That commit was already running. |
| `failed` | 1 | The update failed. The error is printed. The previous version is running if a rollback was possible. |
| (timeout) | 2 | No result within the timeout. Check the server. |

The job has `timeout-minutes: 30` as an outer limit.

### What a successful run means

A green Deploy run means the new version **was built, started and passed its
health checks** on the server. It does not check the website content itself.

## One-time setup

You need to do these once. They are repository settings, not files.

### 1. Server: updater reachable

The updater must be running (see [`updater/README.md`](../../updater/README.md))
and the host nginx must route `/hooks/` to it, so
`https://athenlyx.com/hooks/update` reaches the updater. The WAF must not block
or challenge `POST /hooks/*` requests from GitHub's runners.

Quick test from any machine:

```bash
UPDATE_SECRET=... scripts/update-request.sh status https://athenlyx.com
```

### 2. GitHub: environment and secret

Repository → **Settings → Environments → New environment** → name it `production`.

1. Under **Deployment branches and tags**, choose **Selected branches and tags** and add `main`.
   Only workflows running on `main` can then use this environment and its secret.
2. Add an **environment secret** named `UPDATE_SECRET` with the **same value** as `UPDATE_SECRET` in the
   server's `.env`. Generate one with `openssl rand -hex 32`.
3. Optional: add an environment **variable** `UPDATE_BASE_URL` if the updater is not at `https://athenlyx.com`.

Do not add required reviewers if you want fully automatic deployments.

### 3. GitHub: branch protection for `main`

Repository → **Settings → Branches → Add branch ruleset / protection rule** for `main`:

- Require a pull request before merging (approvals: 0 is fine for a one-person repository).
- Require status checks to pass before merging, and select:
  `validate`, `vale`, `secrets`, `preflight`, `images`, `updater-tests`.
  (A check appears in the list only after it has run once. Open a pull request first so they have run.)
- Do not allow bypassing the rules (include administrators). This is what makes "merged" mean "checked".
- Block force pushes and deletion of `main`.

The same with the GitHub CLI (classic branch protection):

```bash
gh api -X PUT repos/PhilT95/athenlyx/branches/main/protection --input - <<'EOF'
{
  "required_status_checks": {
    "strict": false,
    "contexts": ["validate", "vale", "secrets", "preflight", "images", "updater-tests"]
  },
  "enforce_admins": true,
  "required_pull_request_reviews": { "required_approving_review_count": 0 },
  "restrictions": null,
  "allow_force_pushes": false,
  "allow_deletions": false
}
EOF
```

`"strict": false` means a branch does not have to be up to date with `main`
before merging. This fits the merge-commit workflow in `WORKFLOW.md`. Set it to
`true` for stricter behavior.

### 4. Check the result

1. Open a pull request. All six checks should appear and run.
2. Try to merge before they finish: the button should be blocked.
3. After merging, open **Actions → Deploy** and follow the run.

## Helper scripts

Both are in [`scripts/`](../../scripts) and also usable by hand. They need
`bash`, `curl`, `openssl` and `jq` (all present on GitHub's `ubuntu-latest`).

| Script | Purpose |
|---|---|
| `update-request.sh [update\|status] [base-url]` | Sends one signed request to the updater. Defaults: `update`, `http://127.0.0.1:6560`. Needs `UPDATE_SECRET`. |
| `wait-for-update.sh <base-url> <since-epoch> [timeout]` | Polls the status until the update finished. Exit codes 0/1/2 as in the table above. `POLL_INTERVAL` (seconds, default 15) can be overridden. |

The signature format is described in
[`updater/README.md`](../../updater/README.md#authentication). The scripts and
the updater are tested against each other in
`updater/tests/test_scripts.py`.

## Operating the pipeline

| Task | How |
|---|---|
| Redeploy without a new commit | Actions → Deploy → **Run workflow** (branch `main`). The updater reports `up-to-date` if nothing changed. |
| Rotate the secret | Generate a new value, update `UPDATE_SECRET` in the server `.env` (then `docker compose up -d updater`) **and** in the GitHub environment secret. Requests fail with `401` between the two changes. |
| Deploy from another branch (testing) | Not through this workflow. Set `ALLOWED_REF` on the server and call `scripts/update-request.sh` by hand (see the updater README). |
| Emergency change that skips the checks | Temporarily relax the branch protection, push, then restore it. The Deploy workflow still runs. The updater's `--strict` build is the only check left. |
| Pause automatic deployments | Disable the Deploy workflow in the Actions tab. |

## Troubleshooting

| Symptom | Likely cause and fix |
|---|---|
| Deploy fails at **Trigger update** with `401` | `UPDATE_SECRET` differs between GitHub and the server's `.env`, or the server clock is more than 5 minutes off. Check `docker logs athenlyx-updater-1` for `Rejected request ...: <reason>`. |
| `403` or an HTML page instead of JSON | The WAF or nginx blocks the request. Allow `POST/GET /hooks/*` and make sure it reaches the updater. |
| `curl: (22)` or `502` | Updater container not running, or wrong `proxy_pass` port. Check `docker compose ps` and `UPDATER_PORT`. |
| Deploy fails at **Wait**, `Update FAILED: ...` | The error text comes from the updater (build error, unhealthy container). See the printed log or `docker logs`. The previous version stays active if a rollback was possible. |
| `Timed out ...` | The build takes longer than 20 minutes, or the updater was restarted during the update. Check the server and trigger again. |
| Workflow does not start | Deploy only runs on `main`. Check that the push was to `main` and the workflow is enabled. |
| Secret is empty in the job | The environment is not named `production`, the secret was added as a repository secret instead of an environment secret, or the branch is not allowed in the environment's branch rules. |
| A required check never appears in branch protection | The check must have run at least once. Open a pull request first. |

## Design decisions and limitations

- **No registry.** The server builds the images from Git. The workflows never build production images. Moving to another Git host means replacing the workflow files and changing `REPO_URL` on the server. The updater and scripts do not change.
- **The workflow does not choose what is deployed.** It only says "update now". The updater deploys the newest commit of the configured branch.
- **Gating relies on branch protection.** If protection is removed or bypassed, unchecked commits on `main` are deployed. The only remaining safety net is the updater's `zensical build --strict` and its rollback on unhealthy containers.
- **Deploy waits for health, not content.** A green run means the containers started and are healthy.
- **Runner-to-server traffic is public.** GitHub runners use changing IP addresses, so IP allow-listing is impractical. The signature and timestamp are the protection.
- **Classic builder.** The updater and the `images` job use Docker's classic (legacy) builder. Docker has deprecated it and plans to remove it in a future release. If the `images` job starts failing because of that, the updater's build step needs to move to BuildKit (see the updater README).
- **Fork pull requests** do not receive repository secrets. They cannot deploy and do not need to: only `main` deploys.
