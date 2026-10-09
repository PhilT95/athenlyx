"""
AthenlyX updater

POST /hooks/update          — trigger an update of the site (HMAC-authenticated)
GET  /hooks/update/status   — current version and last result (HMAC-authenticated)
GET  /hooks/health          — unauthenticated liveness check

The updater always deploys the tip of ALLOWED_REF from REPO_URL. The request
payload never selects what gets built, so a valid trigger can only ever
(re)deploy what is already on the protected branch.

Authentication headers:
  X-Timestamp:  unix time in seconds
  X-Signature:  sha256=<hex HMAC-SHA256 of "<timestamp>.<raw body>" using UPDATE_SECRET>
"""

import json
import logging

from fastapi import FastAPI, Header, HTTPException, Request, status

from auth import AuthError, Verifier
from config import Config
from runner import Runner

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s  %(levelname)-8s  %(message)s",
    datefmt="%Y-%m-%dT%H:%M:%S",
)

cfg = Config.from_env()
verifier = Verifier(cfg.update_secret, cfg.max_clock_skew)
runner = Runner(cfg)

app = FastAPI(title="AthenlyX Updater", docs_url=None, redoc_url=None, openapi_url=None)


async def _authenticate(request: Request, timestamp: str | None, signature: str | None) -> bytes:
    body = await request.body()
    try:
        verifier.verify(timestamp, signature, body)
    except AuthError as exc:
        logging.getLogger("updater").warning("Rejected request from %s: %s",
                                             request.client.host if request.client else "?", exc)
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, "Unauthorized.") from None
    return body


@app.post("/hooks/update", status_code=status.HTTP_202_ACCEPTED)
async def update(
    request: Request,
    x_timestamp: str | None = Header(None),
    x_signature: str | None = Header(None),
):
    body = await _authenticate(request, x_timestamp, x_signature)

    ref = None
    if body:
        try:
            payload = json.loads(body)
            ref = payload.get("ref") if isinstance(payload, dict) else None
        except ValueError:
            raise HTTPException(status.HTTP_400_BAD_REQUEST, "Body must be JSON.") from None
    if ref and ref != cfg.allowed_ref:
        return {"status": "ignored", "reason": f"Only {cfg.allowed_ref} is deployed."}

    return {"status": runner.trigger()}


@app.get("/hooks/update/status")
async def update_status(
    request: Request,
    x_timestamp: str | None = Header(None),
    x_signature: str | None = Header(None),
):
    await _authenticate(request, x_timestamp, x_signature)
    return runner.status()


@app.get("/hooks/health")
def health():
    return {"status": "ok"}
