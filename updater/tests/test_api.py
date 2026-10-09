import time

import pytest
from fastapi.testclient import TestClient

import main
from auth import Verifier, sign

SECRET = main.cfg.update_secret


@pytest.fixture
def client(monkeypatch):
    calls = []
    monkeypatch.setattr(main, "verifier", Verifier(SECRET))
    monkeypatch.setattr(main.runner, "trigger", lambda: calls.append(1) or "started")
    c = TestClient(main.app)
    c.calls = calls
    return c


def _headers(body=b"", secret=SECRET):
    ts = str(int(time.time()))
    return {"X-Timestamp": ts, "X-Signature": sign(secret, ts, body)}


def test_health_is_public(client):
    assert client.get("/hooks/health").status_code == 200


def test_update_requires_auth(client):
    assert client.post("/hooks/update", content=b"{}").status_code == 401
    assert client.calls == []


def test_update_rejects_bad_signature(client):
    r = client.post("/hooks/update", content=b"{}", headers=_headers(b"{}", "x" * 40))
    assert r.status_code == 401 and client.calls == []


def test_update_triggers(client):
    body = b'{"ref":"refs/heads/main"}'
    r = client.post("/hooks/update", content=body, headers=_headers(body))
    assert r.status_code == 202 and r.json() == {"status": "started"}
    assert client.calls == [1]


def test_other_ref_ignored(client):
    body = b'{"ref":"refs/heads/docs"}'
    r = client.post("/hooks/update", content=body, headers=_headers(body))
    assert r.status_code == 202 and r.json()["status"] == "ignored"
    assert client.calls == []


def test_invalid_json_rejected(client):
    body = b"not json"
    assert client.post("/hooks/update", content=body, headers=_headers(body)).status_code == 400


def test_payload_cannot_select_what_is_built(client):
    body = b'{"ref":"refs/heads/main","sha":"deadbeef","repo":"https://evil.example/x.git"}'
    assert client.post("/hooks/update", content=body, headers=_headers(body)).status_code == 202


def test_status_requires_auth_and_works(client):
    assert client.get("/hooks/update/status").status_code == 401
    r = client.get("/hooks/update/status", headers=_headers())
    assert r.status_code == 200 and "current_tag" in r.json()
