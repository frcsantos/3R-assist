"""AuthService — HMAC-signed magic-link and session tokens (F08).

Tokens are URL-safe `base64url(payload).signature` strings signed with
AUTH_SECRET. Raw tokens are never persisted; repositories store only
their SHA-256 hashes. Magic-link tokens are single-use (enforced in the
database) and session tokens are validated against user_sessions.
"""

from __future__ import annotations

import base64
import hashlib
import hmac
import json
import secrets
import time
from typing import Any

from app.config import get_settings

MAGIC_LINK_TTL_SECONDS = 30 * 60  # 30 minutes
SESSION_TTL_SECONDS = 30 * 24 * 60 * 60  # 30 days


class AuthError(ValueError):
    """Raised when a token is malformed, tampered with, or expired."""


def _secret() -> str:
    secret = get_settings().auth_secret
    if secret:
        return secret
    # Development fallback: random per-process secret. Sessions will not
    # survive a restart — acceptable only while the user system is off.
    return "dev-insecure-" + secrets.token_hex(16)


def _b64_encode(raw: bytes) -> str:
    return base64.urlsafe_b64encode(raw).rstrip(b"=").decode("ascii")


def _b64_decode(value: str) -> bytes:
    padding = "=" * (-len(value) % 4)
    return base64.urlsafe_b64decode(value + padding)


class AuthService:
    def __init__(self, secret: str | None = None) -> None:
        self._secret = (secret or _secret()).encode("utf-8")

    # -- token primitives --------------------------------------------------

    def _sign(self, payload: dict[str, Any]) -> str:
        body = _b64_encode(json.dumps(payload).encode("utf-8"))
        signature = hmac.new(self._secret, body.encode("ascii"), hashlib.sha256)
        return f"{body}.{_b64_encode(signature.digest())}"

    def _unsign(self, token: str) -> dict[str, Any]:
        try:
            body, signature = token.split(".", 1)
        except ValueError as exc:
            raise AuthError("Malformed token.") from exc
        expected = hmac.new(self._secret, body.encode("ascii"), hashlib.sha256)
        actual = _b64_decode(signature)
        if not hmac.compare_digest(expected.digest(), actual):
            raise AuthError("Token signature is invalid.")
        try:
            payload = json.loads(_b64_decode(body))
        except (ValueError, TypeError) as exc:
            raise AuthError("Token payload is invalid.") from exc
        if not isinstance(payload, dict):
            raise AuthError("Token payload is invalid.")
        exp = payload.get("exp")
        if not isinstance(exp, (int, float)) or time.time() > float(exp):
            raise AuthError("Token has expired.")
        return payload

    @staticmethod
    def hash_token(token: str) -> str:
        """SHA-256 hex digest of a raw token, for persistence."""
        return hashlib.sha256(token.encode("utf-8")).hexdigest()

    # -- magic links -------------------------------------------------------

    def issue_magic_link_token(self, email: str) -> str:
        return self._sign(
            {
                "kind": "magic_link",
                "email": email,
                "exp": time.time() + MAGIC_LINK_TTL_SECONDS,
            }
        )

    def verify_magic_link_token(self, token: str) -> str:
        payload = self._unsign(token)
        email = payload.get("email")
        if payload.get("kind") != "magic_link" or not isinstance(email, str):
            raise AuthError("Not a magic-link token.")
        return email

    # -- sessions ----------------------------------------------------------

    def issue_session_token(self, user_id: int) -> str:
        return self._sign(
            {
                "kind": "session",
                "sub": user_id,
                "exp": time.time() + SESSION_TTL_SECONDS,
            }
        )

    def verify_session_token(self, token: str) -> int:
        payload = self._unsign(token)
        sub = payload.get("sub")
        if payload.get("kind") != "session" or not isinstance(sub, int):
            raise AuthError("Not a session token.")
        return sub
