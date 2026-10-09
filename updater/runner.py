"""Update logic: fetch the source, build the images, recreate the services, roll back on failure."""

import json
import logging
import os
import shutil
import subprocess
import tempfile
import threading
from collections import deque
from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from pathlib import Path

from config import Config

log = logging.getLogger("updater")


class UpdateError(Exception):
    pass


@dataclass
class State:
    current_sha: str | None = None
    current_tag: str | None = None
    previous_tag: str | None = None
    last_result: dict | None = None


def _now() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


class Runner:
    def __init__(self, cfg: Config) -> None:
        self.cfg = cfg
        self._state_file = Path(cfg.state_dir) / "state.json"
        self.state = self._load_state()
        self.lines: deque[str] = deque(maxlen=200)
        self._mu = threading.Lock()
        self._running = False
        self._pending = False

    # ------------------------------------------------------------------
    # Triggering: one update at a time; requests arriving meanwhile are
    # coalesced into a single follow-up run.
    # ------------------------------------------------------------------

    @property
    def running(self) -> bool:
        return self._running

    def trigger(self) -> str:
        with self._mu:
            if self._running:
                self._pending = True
                return "queued"
            self._running = True
        threading.Thread(target=self._loop, name="update", daemon=True).start()
        return "started"

    def _loop(self) -> None:
        while True:
            try:
                self.run_once()
            except Exception:
                log.exception("Unexpected error during update.")
            with self._mu:
                if self._pending:
                    self._pending = False
                    continue
                self._running = False
                return

    # ------------------------------------------------------------------
    # One update run
    # ------------------------------------------------------------------

    def run_once(self) -> None:
        started = _now()
        workdir = None
        try:
            Path(self.cfg.work_dir).mkdir(parents=True, exist_ok=True)
            workdir = tempfile.mkdtemp(prefix="src-", dir=self.cfg.work_dir)
            sha = self._fetch(workdir)

            if sha == self.state.current_sha:
                self._say(f"Already running {sha[:12]}; nothing to do.")
                self._record("up-to-date", sha, started)
                return

            tag = sha[:12]
            self._say(f"Building {tag} …")
            self._build(workdir, tag)

            previous = self.state.current_tag
            self._say(f"Starting {tag} …")
            try:
                self._compose_up(tag)
            except UpdateError as exc:
                self._say(f"Start failed: {exc}")
                if previous:
                    self._say(f"Rolling back to {previous} …")
                    try:
                        self._compose_up(previous)
                    except UpdateError as rb:
                        self._say(f"Rollback failed too: {rb}")
                raise

            self.state.previous_tag = previous
            self.state.current_tag = tag
            self.state.current_sha = sha
            self._record("success", sha, started)
            self._say(f"Now running {tag}.")
            self._prune()
        except Exception as exc:
            self._say(f"Update failed: {exc}")
            self._record("failed", None, started, error=str(exc))
        finally:
            if workdir:
                shutil.rmtree(workdir, ignore_errors=True)

    # ------------------------------------------------------------------
    # Steps (each is small so tests can replace them)
    # ------------------------------------------------------------------

    def _fetch(self, workdir: str) -> str:
        self._say(f"Fetching {self.cfg.allowed_ref} from {self.cfg.repo_url} …")
        self._run(["git", "init", "-q", workdir])
        # "origin" is read by the SEO plugin; the full history (no --depth) gives
        # it real creation/modification dates and authors per page.
        self._run(["git", "-C", workdir, "remote", "add", "origin", self.cfg.repo_url])
        self._run(
            ["git", "-C", workdir, "fetch", "-q", "--no-tags", "origin", self.cfg.allowed_ref],
            timeout=300,
        )
        sha = self._run(["git", "-C", workdir, "rev-parse", "FETCH_HEAD"]).strip()
        self._run(["git", "-C", workdir, "checkout", "-q", "--detach", "FETCH_HEAD"])
        return sha

    def _build(self, context: str, tag: str) -> None:
        import docker

        client = docker.from_env(timeout=self.cfg.build_timeout)
        try:
            for service in self.cfg.services:
                image = f"{self.cfg.compose_project}-{service}:{tag}"
                self._say(f"Building image {image} …")
                stream = client.api.build(
                    path=context, tag=image, target=service,
                    rm=True, forcerm=True, decode=True,
                )
                for chunk in stream:
                    if "error" in chunk:
                        raise UpdateError(f"Build of {image} failed: {chunk['error'].strip()}")
                    line = chunk.get("stream", "").strip()
                    if line.startswith("Step "):
                        self._say(line)
        except docker.errors.DockerException as exc:
            raise UpdateError(f"Docker build error: {exc}") from exc
        finally:
            client.close()

    def _compose_up(self, tag: str) -> None:
        cmd = [
            "docker", "compose",
            "-p", self.cfg.compose_project,
            "-f", self.cfg.compose_file,
            "--project-directory", str(Path(self.cfg.compose_file).parent),
            "up", "-d", "--no-build", "--no-deps", "--pull", "never",
            "--wait", "--wait-timeout", str(self.cfg.health_timeout),
            *self.cfg.services,
        ]
        self._run(cmd, env={"IMAGE_TAG": tag}, timeout=self.cfg.health_timeout + 60)

    def _prune(self) -> None:
        """Remove old images, keeping the newest N plus the current and previous tags."""
        import docker

        keep_tags = {t for t in (self.state.current_tag, self.state.previous_tag) if t}
        try:
            client = docker.from_env()
            for service in self.cfg.services:
                repo = f"{self.cfg.compose_project}-{service}"
                images = sorted(client.images.list(name=repo),
                                key=lambda i: i.attrs.get("Created", ""), reverse=True)
                for image in images[self.cfg.keep_images:]:
                    for ref in image.tags:
                        name, _, tag = ref.partition(":")
                        if name == repo and tag not in keep_tags:
                            client.images.remove(ref)
                            self._say(f"Removed old image {ref}.")
            client.close()
        except Exception as exc:  # pruning must never fail an update
            self._say(f"Image pruning skipped: {exc}")

    # ------------------------------------------------------------------
    # Helpers
    # ------------------------------------------------------------------

    def _run(self, cmd: list[str], env: dict | None = None, timeout: int = 120) -> str:
        full_env = {**os.environ, "GIT_TERMINAL_PROMPT": "0", **(env or {})}
        try:
            res = subprocess.run(cmd, capture_output=True, text=True, timeout=timeout, env=full_env)
        except subprocess.TimeoutExpired:
            raise UpdateError(f"'{cmd[0]} {cmd[1] if len(cmd) > 1 else ''}' timed out after {timeout}s.") from None
        if res.returncode != 0:
            detail = (res.stderr or res.stdout).strip().splitlines()[-5:]
            raise UpdateError(f"'{' '.join(cmd[:3])}' exited with {res.returncode}: {' | '.join(detail)}")
        return res.stdout

    def _say(self, msg: str) -> None:
        log.info(msg)
        self.lines.append(f"{_now()} {msg}")

    def _record(self, outcome: str, sha: str | None, started: str, error: str | None = None) -> None:
        self.state.last_result = {
            "outcome": outcome, "sha": sha, "started": started, "finished": _now(),
            **({"error": error} if error else {}),
        }
        self._save_state()

    def _load_state(self) -> State:
        try:
            return State(**json.loads(self._state_file.read_text()))
        except (FileNotFoundError, ValueError, TypeError):
            return State()

    def _save_state(self) -> None:
        try:
            self._state_file.parent.mkdir(parents=True, exist_ok=True)
            tmp = self._state_file.with_suffix(".tmp")
            tmp.write_text(json.dumps(asdict(self.state)))
            tmp.replace(self._state_file)
        except OSError as exc:
            log.error("Could not persist state: %s", exc)

    def status(self) -> dict:
        return {
            "running": self._running,
            "pending": self._pending,
            **asdict(self.state),
            "log": list(self.lines)[-30:],
        }
