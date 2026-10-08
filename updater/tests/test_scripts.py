"""End-to-end tests of scripts/update-request.sh and scripts/wait-for-update.sh
against a real (in-process) updater HTTP server."""

import os
import shutil
import socket
import subprocess
import threading
import time
from datetime import datetime, timezone
from pathlib import Path

import pytest
import uvicorn

import main
from auth import Verifier

SCRIPTS = Path(__file__).resolve().parents[2] / "scripts"
SECRET = main.cfg.update_secret

pytestmark = pytest.mark.skipif(
    not all(shutil.which(t) for t in ("bash", "curl", "openssl", "jq")),
    reason="needs bash, curl, openssl and jq",
)


@pytest.fixture
def server(monkeypatch):
    monkeypatch.setattr(main, "verifier", Verifier(SECRET))  # fresh replay cache
    triggered = []
    monkeypatch.setattr(main.runner, "trigger", lambda: triggered.append(1) or "started")
    monkeypatch.setattr(main.runner, "_save_state", lambda: None)

    with socket.socket() as s:
        s.bind(("127.0.0.1", 0))
        port = s.getsockname()[1]
    srv = uvicorn.Server(uvicorn.Config(main.app, host="127.0.0.1", port=port, log_level="error"))
    thread = threading.Thread(target=srv.run, daemon=True)
    thread.start()
    for _ in range(100):
        if srv.started:
            break
        time.sleep(0.05)
    yield f"http://127.0.0.1:{port}", triggered
    srv.should_exit = True
    thread.join(5)


def _run(script, *args, secret=SECRET, **env):
    return subprocess.run(
        [str(SCRIPTS / script), *args],
        capture_output=True, text=True, timeout=30,
        env={**os.environ, "UPDATE_SECRET": secret, **env},
    )


def _set_result(outcome, finished_offset=0, error=None):
    when = datetime.fromtimestamp(time.time() + finished_offset, timezone.utc)
    main.runner.state.last_result = {
        "outcome": outcome, "sha": "a" * 40, "started": when.isoformat(timespec="seconds"),
        "finished": when.isoformat(timespec="seconds"), **({"error": error} if error else {}),
    }
    main.runner.state.current_tag = "aaaaaaaaaaaa"
    main.runner._running = False
    main.runner._pending = False


def test_update_request_is_accepted(server):
    url, triggered = server
    res = _run("update-request.sh", "update", url)
    assert res.returncode == 0, res.stderr
    assert '"status":"started"' in res.stdout
    assert triggered == [1]


def test_update_request_with_wrong_secret_is_rejected(server):
    url, triggered = server
    res = _run("update-request.sh", "update", url, secret="x" * 40)
    assert res.returncode != 0 and triggered == []


def test_status_request(server):
    url, _ = server
    res = _run("update-request.sh", "status", url)
    assert res.returncode == 0 and '"current_tag"' in res.stdout


def test_wait_succeeds(server):
    url, _ = server
    _set_result("success")
    res = _run("wait-for-update.sh", url, str(int(time.time()) - 10), "20", POLL_INTERVAL="1")
    assert res.returncode == 0, res.stdout + res.stderr
    assert "Update finished: success" in res.stdout


def test_wait_accepts_up_to_date(server):
    url, _ = server
    _set_result("up-to-date")
    assert _run("wait-for-update.sh", url, str(int(time.time()) - 10), "20", POLL_INTERVAL="1").returncode == 0


def test_wait_reports_failure(server):
    url, _ = server
    _set_result("failed", error="build broke")
    res = _run("wait-for-update.sh", url, str(int(time.time()) - 10), "20", POLL_INTERVAL="1")
    assert res.returncode == 1
    assert "build broke" in res.stdout


def test_wait_ignores_result_older_than_trigger_and_times_out(server):
    url, _ = server
    _set_result("success", finished_offset=-3600)
    res = _run("wait-for-update.sh", url, str(int(time.time())), "3", POLL_INTERVAL="1")
    assert res.returncode == 2


def test_wait_keeps_waiting_while_running(server):
    url, _ = server
    _set_result("success")
    main.runner._running = True
    res = _run("wait-for-update.sh", url, str(int(time.time()) - 10), "3", POLL_INTERVAL="1")
    assert res.returncode == 2 and "in progress" in res.stdout
