![Image](/docs/images/general/athenlyx-high-resolution-logo_banner.png)

# Welcome to AthenlyX.com Github

[![Build Check](https://github.com/PhilT95/athenlyx/actions/workflows/build.yml/badge.svg)](https://github.com/PhilT95/athenlyx/actions/workflows/build.yml)
[![Security Check](https://github.com/PhilT95/athenlyx/actions/workflows/security.yml/badge.svg)](https://github.com/PhilT95/athenlyx/actions/workflows/security.yml)
[![Vale Linter](https://github.com/PhilT95/athenlyx/actions/workflows/vale.yml/badge.svg)](https://github.com/PhilT95/athenlyx/actions/workflows/vale.yml)

This is the git repository the website [AthenlyX.com](https://athenlyx.com) is build from using [Zensical](https://zensical.org/). If you want to use this repository as a base for your documentation, please make sure you adapt and change all domain-specific values and don't forget to change the documents with yours!


Since this project mostly contains markdown documents that are compiled to webpages using MkDocs, there are no vulnerabilities affecting this project at this time. Vulnerabilities related to used services and products that this project is based on are not listed here.


If you want to find out about how the Website is hosted and the infrastructure behind it, please refer to the website itself. (Way easier to navigate)

## Deployment

The website runs in Docker. After a merge to `main` the server builds and deploys the new version by itself and rolls back if it does not start. See [Zensical in Docker with automatic updates](docs/services/zensical/zensical_docker_deployment.md) for the setup, and the technical documentation of the parts:

- [`updater/`](updater/README.md): the service that performs the updates
- [`api/`](api/README.md): the content API for bots and AI agents
- [`.github/workflows/`](.github/workflows/README.md): the CI/CD pipeline and GitHub settings

## Local preview

```sh
pip install -r requirements.txt
zensical serve
```

