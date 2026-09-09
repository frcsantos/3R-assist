"""User system (F08) — feature-flag gating and token service.

The user system must remain unavailable (404 on /auth/*, enabled=false on
/auth/status) until USER_SYSTEM_ENABLED is set. These tests cover both the
disabled state (default) and the enabled flow with faked dependencies.
"""

from __future__ import annotations

from datetime import datetime, timezone

import pytest
from fastapi.testclient import TestClient

from app.api import deps as deps_module
from app.api.routes import auth as auth_routes_module
from app.main import create_app
from app.models.user import User
from app.repositories.users import UserRepository
from app.services.auth import AuthError, AuthService


def _client() -> TestClient:
    app = create_app()
    app.dependency_overrides.clear()
    return TestClient(app)


# -- disabled by default -----------------------------------------------------


def test_status_reports_disabled_by_default():
    with _client() as client:
        response = client.get("/auth/status")
    assert response.status_code == 200
    assert response.json() == {"enabled": False}


@pytest.mark.parametrize(
    ("method", "path", "kwargs"),
    [
        ("get", "/auth/me", {}),
        ("post", "/auth/magic-link", {"json": {"email": "a@b.org"}}),
        ("post", "/auth/verify", {"json": {"token": "whatever"}}),
        ("post", "/auth/logout", {}),
    ],
)
def test_gated_endpoints_are_404_while_disabled(method, path, kwargs):
    with _client() as client:
        response = getattr(client, method)(path, **kwargs)
    assert response.status_code == 404


# -- token service (pure, no DB) ---------------------------------------------


def test_magic_link_token_roundtrip():
    auth = AuthService(secret="test-secret")
    token = auth.issue_magic_link_token("researcher@example.org")
    assert auth.verify_magic_link_token(token) == "researcher@example.org"


def test_session_token_roundtrip():
    auth = AuthService(secret="test-secret")
    token = auth.issue_session_token(42)
    assert auth.verify_session_token(token) == 42


def test_tampered_token_is_rejected():
    auth = AuthService(secret="test-secret")
    token = auth.issue_magic_link_token("researcher@example.org")
    tampered = token[:-1] + ("A" if token[-1] != "A" else "B")
    with pytest.raises(AuthError):
        auth.verify_magic_link_token(tampered)


def test_expired_token_is_rejected(monkeypatch):
    auth = AuthService(secret="test-secret")
    token = auth.issue_magic_link_token("researcher@example.org")

    import app.services.auth as auth_module

    monkeypatch.setattr(auth_module.time, "time", lambda: 2**40)
    with pytest.raises(AuthError):
        auth.verify_magic_link_token(token)


def test_wrong_kind_token_is_rejected():
    auth = AuthService(secret="test-secret")
    session = auth.issue_session_token(1)
    with pytest.raises(AuthError):
        auth.verify_magic_link_token(session)


# -- enabled flow with faked repository --------------------------------------


class FakeSettings:
    user_system_enabled = True
    database_url = "postgresql://fake"
    app_env = "development"
    app_base_url = "http://localhost:5173"
    email_provider_api_key = None
    email_from_address = None


class FakeUserRepository(UserRepository):
    def __init__(self) -> None:
        self.user = User(
            id=1,
            email="researcher@example.org",
            created_at=datetime(2026, 1, 1, tzinfo=timezone.utc),
            last_seen_at=datetime(2026, 1, 1, tzinfo=timezone.utc),
        )
        self.magic_links: set[str] = set()
        self.sessions: dict[str, int] = {}

    async def get_or_create_user(self, email: str) -> User:
        return self.user.model_copy(update={"email": email})

    async def create_magic_link_token(self, user_id: int, token_hash: str) -> None:
        self.magic_links.add(token_hash)

    async def consume_magic_link_token(self, token_hash: str) -> int | None:
        if token_hash not in self.magic_links:
            return None
        self.magic_links.discard(token_hash)
        return self.user.id

    async def create_session(self, user_id: int, token_hash: str) -> None:
        self.sessions[token_hash] = user_id

    async def find_session(self, token_hash: str) -> int | None:
        return self.sessions.get(token_hash)

    async def revoke_session(self, token_hash: str) -> None:
        self.sessions.pop(token_hash, None)

    async def get_user(self, user_id: int) -> User | None:
        return self.user if user_id == self.user.id else None


@pytest.fixture
def enabled_app(monkeypatch):
    monkeypatch.setattr(auth_routes_module, "get_settings", lambda: FakeSettings())
    monkeypatch.setattr(deps_module, "get_settings", lambda: FakeSettings())
    repository = FakeUserRepository()
    app = create_app()
    app.dependency_overrides[deps_module.get_user_repository] = lambda: repository
    app.dependency_overrides[deps_module.get_auth_service] = lambda: AuthService(
        secret="test-secret"
    )
    with TestClient(app) as client:
        yield client
    app.dependency_overrides.clear()


def test_enabled_status_endpoint(monkeypatch):
    monkeypatch.setattr(auth_routes_module, "get_settings", lambda: FakeSettings())
    with _client() as client:
        response = client.get("/auth/status")
    assert response.json() == {"enabled": True}


def test_enabled_full_magic_link_flow(enabled_app):
    client = enabled_app

    # 1. Request a magic link — development mode returns the link directly.
    response = client.post(
        "/auth/magic-link", json={"email": "researcher@example.org"}
    )
    assert response.status_code == 200
    body = response.json()
    assert body["dev_login_link"].startswith("http://localhost:5173/auth?token=")
    token = body["dev_login_link"].split("token=", 1)[1]

    # 2. Verify the link — single use; a session token is issued.
    response = client.post("/auth/verify", json={"token": token})
    assert response.status_code == 200
    session = response.json()
    assert session["user"]["email"] == "researcher@example.org"
    assert session["token"]

    # Replay is rejected.
    response = client.post("/auth/verify", json={"token": token})
    assert response.status_code == 401

    # 3. /auth/me with the session token.
    bearer = {"Authorization": f"Bearer {session['token']}"}
    response = client.get("/auth/me", headers=bearer)
    assert response.status_code == 200
    assert response.json()["email"] == "researcher@example.org"

    # Without credentials it is 401.
    response = client.get("/auth/me")
    assert response.status_code == 401

    # 4. Logout revokes the session.
    response = client.post("/auth/logout", headers=bearer)
    assert response.status_code == 204
    response = client.get("/auth/me", headers=bearer)
    assert response.status_code == 401
