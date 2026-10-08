"""Updater configuration, read once from environment variables."""

import os
from dataclasses import dataclass


def _int(name: str, default: int) -> int:
    return int(os.environ.get(name, default))


@dataclass(frozen=True)
class Config:
    repo_url: str
    update_secret: str
    allowed_ref: str = "refs/heads/main"
    keep_images: int = 3
    compose_file: str = "/deploy/compose.yaml"
    compose_project: str = "athenlyx"
    # Compose services that are rebuilt and recreated. Each name is also the
    # Dockerfile target, and the image is named "<project>-<service>:<tag>"
    # (matching the image names in compose.yaml).
    services: tuple[str, ...] = ("api", "web")
    state_dir: str = "/state"
    work_dir: str = "/work"
    health_timeout: int = 180
    build_timeout: int = 1800
    max_clock_skew: int = 300

    @classmethod
    def from_env(cls) -> "Config":
        repo_url = os.environ.get("REPO_URL", "")
        secret = os.environ.get("UPDATE_SECRET", "")
        if not repo_url:
            raise RuntimeError("REPO_URL environment variable must be set.")
        if len(secret) < 32:
            raise RuntimeError("UPDATE_SECRET must be set and at least 32 characters long.")
        return cls(
            repo_url=repo_url,
            update_secret=secret,
            allowed_ref=os.environ.get("ALLOWED_REF", cls.allowed_ref),
            keep_images=_int("KEEP_IMAGES", cls.keep_images),
            compose_file=os.environ.get("COMPOSE_FILE", cls.compose_file),
            compose_project=os.environ.get("COMPOSE_PROJECT", cls.compose_project),
            state_dir=os.environ.get("STATE_DIR", cls.state_dir),
            work_dir=os.environ.get("WORK_DIR", cls.work_dir),
            health_timeout=_int("HEALTH_TIMEOUT", cls.health_timeout),
            build_timeout=_int("BUILD_TIMEOUT", cls.build_timeout),
        )
