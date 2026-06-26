# Requirements

## Prerequisites

- **Python** 3.10 or later
- **pip** (included with Python)

## Installation

```sh
pip install zensical
pip install mkdocs-ultralytics-plugin
```

Zensical bundles all its dependencies automatically — no additional packages are needed.

## Usage

| Command | Description |
|---------|-------------|
| `zensical serve` | Start local preview server at `localhost:8000` |
| `zensical build` | Build static site to `site/` directory |
| `zensical build --strict` | Build with strict mode (fails on warnings) |

## CI/CD

The GitHub Actions workflow (`.github/workflows/build.yml`) runs `zensical build --strict` on every push. No manual dependency installation beyond `pip install zensical`.
