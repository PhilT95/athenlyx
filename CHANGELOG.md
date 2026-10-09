# Changelog

All notable technical changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [2.0.0] - 2026-10-09

### Added

- Added a Docker setup for the website
    - Multi-stage `Dockerfile` with the targets `api` and `web`; the site build includes the Ultralytics SEO step and uses the Git history for page dates
    - `compose.yaml` with the services `web`, `api`, `updater` and `docker-proxy`; ports are bound to `127.0.0.1` and configurable in `.env`
    - nginx configuration for the `web` container (`docker/nginx.conf`)
    - `.dockerignore` and `.env.example`
- Added the updater service (`updater/`)
    - `POST /hooks/update` and `GET /hooks/update/status`, authenticated with an HMAC-SHA256 signature and a timestamp with replay protection
    - Always deploys the newest commit of the configured branch from the configured repository; the request cannot select the source
    - Builds the images on the server, replaces the containers, waits for the health checks and rolls back on failure
    - Combines concurrent requests, keeps the last images for rollbacks and stores its state in a volume
    - Access to Docker through `docker-socket-proxy` instead of the Docker socket
    - 36 automated tests
- Added the GitHub workflow `deploy.yml`, which triggers the update after a push to `main` and waits for the result
- Added the GitHub workflow `docker.yml`, which builds and tests the images and runs the updater tests
- Added the helper scripts `update-request.sh`, `wait-for-update.sh` and `test-buildkit-proxy.sh`
- Added `deploy/nginx-host.conf` as a reference for the host nginx
- Added technical documentation in `api/README.md`, `updater/README.md` and `.github/workflows/README.md`
- Added the guide "Zensical in Docker with automatic updates" to the website

### Changed

- Changed the deployment from a script on the server (`sync.sh`) to Docker containers that update themselves after a merge to `main`
- Changed the API to a read-only content service; it is built into the container image together with the site
- Changed the Build Check and Security Check workflows to also run on pull requests, so they can be required checks
- Changed the Zensical version to be defined only in `requirements.txt`; the `Dockerfile` and the Build Check workflow install it from there
- Updated `README.md`, `REQUIREMENTS.md` and `WORKFLOW.md` for the new setup
- Updated the MkDocs auto-update and Zensical setup guides to point to the Docker guide

### Removed

- Removed `scripts/sync.sh` and the cron-based update
- Removed the `/hooks/deploy` endpoint, `DEPLOY_TOKEN` and `SYNC_SCRIPT` from the API
- Removed the systemd unit and environment template of the API (`api/api.service`, `api/api.env.example`)
- Removed the standalone webhook files (`deploy/hooks.yaml`, `deploy/webhook.service`, `deploy/nginx-webhook.conf`) and the old `deploy/nginx-api.conf`
- Removed the manual `deploy/deploy.yml` workflow

### Fixed

- Fixed the API search index loading: it now reads the `search.json` that Zensical creates instead of the MkDocs `search/search_index.json`

### Security

- The updater has no access to the Docker socket and its containers run with `no-new-privileges`
- Update requests are authenticated with a constant-time signature comparison instead of a static token comparison

## [1.1.1] - 2026-08-29

### Added

- Added Vale Linter with the following styles
    - Vale
    - Google
    - proselint
    - write-good
- Added Vale project scoped vocabularies
- Added CI check for Vale
- Added CI check for Pre-Flight before publishing on PR

### Changed

- Fixed Vale errors and started implementing new documentation standard


### Fixed

- Fixed override (Banner display)




## [1.1.0] - 2026-06-27

### Added

- Integrated Ultralytics for SEO optimization.
- Added GitHub issue templates (bug report and feature request).
- Added a requirements file.

### Changed

- Adapted the Ultralytics and sync scripts.

### Fixed

- Corrected various documentation errors.

## [1.0.0] - 2026-06-25

### Added

- Migrated from Material for MkDocs to Zensical.

### Changed

- Reworked the entire documentation in preparation for the Zensical migration.
- Adapted the build workflow and the sync script.

### Fixed

- Corrected various documentation errors.

## [0.5.0] - 2026-06-17

### Added

- Added GitHub Actions workflows (build and security).
- Added Ansible inventory setup.

### Changed

- Split GitHub Actions into separate pipelines.
- Reworked the announcement banner handling.

## [0.4.0] - 2026-06-08

### Added

- Added the announcement banner.

### Changed

- Reworked the website structure.
- Updated the navigation and related files.

### Fixed

- Fixed mkdocs configuration issues.

## [0.3.0] - 2025-10-29

### Changed

- Restructured the site navigation.

## [0.2.0] - 2025-09-18

### Added

- Configured the mkdocs-glightbox extension.

### Changed

- Changed the website structure.
- Updated the sync script regarding the domain change.

### Fixed

- Fixed compiling errors.

## [0.1.0] - 2025-08-24

### Added

- Introduced the changelog.
- Changed the site to the new domain athenlyx.com.
- Extended MkDocs functionality with the Keyboard Keys function.
- Added a new site logo and favicon.

### Fixed

- Fixed sync script issues.
- Fixed and corrected issues with MkDocs and the documentation.

## [0.0.1] - 2025-07-30

### Added

- Initial site setup with Material for MkDocs.
- Added the mkdocs configuration, navigation and extensions.
- Added the sync script and automation.
- Added abbreviations support.
