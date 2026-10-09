# Requirements

## Prerequisites

- **Python** 3.10 or later
- **pip** (included with Python)

For the production setup in Docker, see [Deployment](#deployment).

## Installation

```sh
pip install -r requirements.txt
```

This installs Zensical in the version used by CI and by the Docker build. Zensical bundles all its dependencies automatically, so no additional packages are needed.

The SEO post-processing step (`scripts/ultralytics.py`) needs `mkdocs-ultralytics-plugin`. It only runs in the Docker build, so you do not need it for local work.

## Usage

| Command | Description |
|---------|-------------|
| `zensical serve` | Start local preview server at `localhost:8000` |
| `zensical build` | Build static site to `site/` directory |
| `zensical build --strict` | Build with strict mode (fails on warnings) |

## Deployment

The website runs in Docker and updates itself after a merge to `main`.

| Requirement | Purpose |
|-------------|---------|
| Docker Engine and the Compose plugin | Run the containers |
| A host nginx (or any reverse proxy) | TLS and routing to the local ports |

```sh
cp .env.example .env      # set UPDATE_SECRET, REPO_URL and the ports
docker compose up -d --build
```

Documentation:

- Setup guide: [`docs/services/zensical/zensical_docker_deployment.md`](docs/services/zensical/zensical_docker_deployment.md)
- Updater service: [`updater/README.md`](updater/README.md)
- Content API: [`api/README.md`](api/README.md)
- CI/CD pipeline and GitHub settings: [`.github/workflows/README.md`](.github/workflows/README.md)

## CI/CD

GitHub Actions runs these checks on every push and pull request:

| Workflow | Check |
|----------|-------|
| `build.yml` | `zensical build --strict` |
| `vale.yml` | Prose linting of `docs/` |
| `security.yml` | Secret scanning with Gitleaks |
| `docker.yml` | The images build and start, and the updater tests pass |
| `preflight.yml` | Pull requests only: changelog and navigation are updated |

A push to `main` runs `deploy.yml`, which asks the updater on the server to deploy the new version.
