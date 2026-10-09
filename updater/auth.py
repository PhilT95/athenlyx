"""Request authentication: HMAC-SHA256 over "<timestamp>.<body>" plus replay protection."""

import hashlib
import hmac
import threading
import time


class AuthError(Exception):
    pass


def sign(secret: str, timestamp: str, body: bytes) -> str:
    mac = hmac.new(secret.encode(), timestamp.encode() + b"." + body, hashlib.sha256)
    return "sha256=" + mac.hexdigest()


class Verifier:
    def __init__(self, secret: str, max_skew: int = 300) -> None:
        self._secret = secret
        self._max_skew = max_skew
        self._seen: dict[str, float] = {}
        self._lock = threading.Lock()

    def verify(self, timestamp: str | None, signature: str | None, body: bytes) -> None:
        if not timestamp or not signature:
            raise AuthError("Missing authentication headers.")
        try:
            ts = int(timestamp)
        except ValueError:
            raise AuthError("Invalid timestamp.") from None

        now = time.time()
        if abs(now - ts) > self._max_skew:
            raise AuthError("Timestamp outside the accepted window.")

        expected = sign(self._secret, timestamp, body)
        if not hmac.compare_digest(expected, signature):
            raise AuthError("Invalid signature.")

        # A valid signature may only be used once within the accepted window.
        with self._lock:
            self._seen = {s: t for s, t in self._seen.items() if now - t <= self._max_skew}
            if signature in self._seen:
                raise AuthError("Replayed request.")
            self._seen[signature] = now
