import threading

import pytest

from config import Config
from runner import Runner, UpdateError

SHA_A = "a" * 40
SHA_B = "b" * 40


@pytest.fixture
def make(tmp_path):
    def _make():
        cfg = Config(repo_url="x", update_secret="s" * 40,
                     state_dir=str(tmp_path / "state"), work_dir=str(tmp_path / "work"))
        r = Runner(cfg)
        r.events = []
        r.sha = SHA_A
        r.fail_up_for = set()
        r._fetch = lambda wd: r.sha
        r._build = lambda ctx, tag: r.events.append(("build", tag))
        r._prune = lambda: r.events.append(("prune",))

        def up(tag):
            r.events.append(("up", tag))
            if tag in r.fail_up_for:
                raise UpdateError("unhealthy")
        r._compose_up = up
        return r
    return _make


def test_first_deploy(make):
    r = make()
    r.run_once()
    assert r.events == [("build", SHA_A[:12]), ("up", SHA_A[:12]), ("prune",)]
    assert r.state.current_sha == SHA_A and r.state.last_result["outcome"] == "success"


def test_same_sha_is_noop(make):
    r = make()
    r.run_once()
    r.events.clear()
    r.run_once()
    assert r.events == [] and r.state.last_result["outcome"] == "up-to-date"


def test_new_sha_updates_and_keeps_previous(make):
    r = make()
    r.run_once()
    r.sha = SHA_B
    r.run_once()
    assert r.state.current_tag == SHA_B[:12] and r.state.previous_tag == SHA_A[:12]


def test_failed_start_rolls_back(make):
    r = make()
    r.run_once()
    r.events.clear()
    r.sha = SHA_B
    r.fail_up_for = {SHA_B[:12]}
    r.run_once()
    assert r.events == [("build", SHA_B[:12]), ("up", SHA_B[:12]), ("up", SHA_A[:12])]
    assert r.state.current_tag == SHA_A[:12]
    assert r.state.last_result["outcome"] == "failed"


def test_build_failure_leaves_running_version(make):
    r = make()
    r.run_once()
    r.events.clear()
    r.sha = SHA_B

    def boom(ctx, tag):
        raise UpdateError("zensical failed")
    r._build = boom
    r.run_once()
    assert r.events == [] and r.state.current_tag == SHA_A[:12]
    assert "zensical failed" in r.state.last_result["error"]


def test_state_persists(make, tmp_path):
    r = make()
    r.run_once()
    r2 = make()
    assert r2.state.current_sha == SHA_A


def test_concurrent_triggers_coalesce(make):
    r = make()
    gate = threading.Event()
    runs = []

    def slow():
        runs.append(1)
        gate.wait(5)
    r.run_once = slow
    assert r.trigger() == "started"
    assert r.trigger() == "queued"
    assert r.trigger() == "queued"
    gate.set()
    for _ in range(100):
        if not r.running:
            break
        threading.Event().wait(0.05)
    assert len(runs) == 2
