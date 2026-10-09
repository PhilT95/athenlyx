import time

import pytest

from auth import AuthError, Verifier, sign

SECRET = "s" * 40


def _ts(offset=0):
    return str(int(time.time()) + offset)


def test_valid_signature_accepted():
    v, ts, body = Verifier(SECRET), _ts(), b'{"ref":"refs/heads/main"}'
    v.verify(ts, sign(SECRET, ts, body), body)


@pytest.mark.parametrize("ts,sig", [(None, "x"), ("1", None), (None, None)])
def test_missing_headers(ts, sig):
    with pytest.raises(AuthError):
        Verifier(SECRET).verify(ts, sig, b"")


def test_wrong_secret_rejected():
    ts = _ts()
    with pytest.raises(AuthError):
        Verifier(SECRET).verify(ts, sign("other" * 10, ts, b""), b"")


def test_tampered_body_rejected():
    ts = _ts()
    sig = sign(SECRET, ts, b"original")
    with pytest.raises(AuthError):
        Verifier(SECRET).verify(ts, sig, b"tampered")


@pytest.mark.parametrize("offset", [-1000, 1000])
def test_old_or_future_timestamp_rejected(offset):
    ts = _ts(offset)
    with pytest.raises(AuthError):
        Verifier(SECRET).verify(ts, sign(SECRET, ts, b""), b"")


def test_non_numeric_timestamp_rejected():
    with pytest.raises(AuthError):
        Verifier(SECRET).verify("abc", sign(SECRET, "abc", b""), b"")


def test_replay_rejected():
    v, ts = Verifier(SECRET), _ts()
    sig = sign(SECRET, ts, b"")
    v.verify(ts, sig, b"")
    with pytest.raises(AuthError, match="Replayed"):
        v.verify(ts, sig, b"")
