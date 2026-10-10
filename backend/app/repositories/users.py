"""UserRepository — auth and account CRUD (Phase 2, F08).

Raw tokens are never stored; only SHA-256 hashes enter the database.
Magic-link tokens are single-use: `consume_magic_link_token` atomically
marks them used so a link cannot be replayed within its validity window.
"""

from __future__ import annotations

from datetime import datetime, timedelta, timezone

from app.db.connection import get_pool
from app.models.user import User

_MAGIC_LINK_TTL = timedelta(minutes=30)
_SESSION_TTL = timedelta(days=30)


def _now() -> datetime:
    return datetime.now(timezone.utc)


class UserRepository:
    async def get_or_create_user(self, email: str) -> User:
        """Return the user with `email`, creating it on first contact."""
        normalized = email.strip().lower()
        pool = await get_pool()
        async with pool.acquire() as conn:
            await conn.execute(
                "INSERT INTO users (email) VALUES ($1) ON CONFLICT (email) DO NOTHING",
                normalized,
            )
            row = await conn.fetchrow(
                """
                SELECT id, email, created_at, last_seen_at
                FROM users WHERE email = $1
                """,
                normalized,
            )
        return User(
            id=row["id"],
            email=row["email"],
            created_at=row["created_at"],
            last_seen_at=row["last_seen_at"],
        )

    async def get_user(self, user_id: int) -> User | None:
        pool = await get_pool()
        async with pool.acquire() as conn:
            row = await conn.fetchrow(
                """
                SELECT id, email, created_at, last_seen_at
                FROM users WHERE id = $1
                """,
                user_id,
            )
        if row is None:
            return None
        return User(
            id=row["id"],
            email=row["email"],
            created_at=row["created_at"],
            last_seen_at=row["last_seen_at"],
        )

    # -- magic links ---------------------------------------------------------

    async def create_magic_link_token(
        self, user_id: int, token_hash: str
    ) -> None:
        pool = await get_pool()
        async with pool.acquire() as conn:
            await conn.execute(
                """
                INSERT INTO magic_link_tokens (user_id, token_hash, expires_at)
                VALUES ($1, $2, $3)
                """,
                user_id,
                token_hash,
                _now() + _MAGIC_LINK_TTL,
            )

    async def consume_magic_link_token(self, token_hash: str) -> int | None:
        """Atomically mark a magic-link token used and return its user.

        Returns None when the token is unknown, already used, or expired.
        """
        pool = await get_pool()
        async with pool.acquire() as conn:
            row = await conn.fetchrow(
                """
                UPDATE magic_link_tokens
                SET used_at = NOW()
                WHERE token_hash = $1
                  AND used_at IS NULL
                  AND expires_at > NOW()
                RETURNING user_id
                """,
                token_hash,
            )
            if row is None:
                return None
            await conn.execute(
                "UPDATE users SET last_seen_at = NOW() WHERE id = $1",
                row["user_id"],
            )
        return row["user_id"]

    # -- sessions ------------------------------------------------------------

    async def create_session(self, user_id: int, token_hash: str) -> None:
        pool = await get_pool()
        async with pool.acquire() as conn:
            await conn.execute(
                """
                INSERT INTO user_sessions (user_id, token_hash, expires_at)
                VALUES ($1, $2, $3)
                """,
                user_id,
                token_hash,
                _now() + _SESSION_TTL,
            )

    async def find_session(self, token_hash: str) -> int | None:
        """Return the user id for a live (unrevoked, unexpired) session."""
        pool = await get_pool()
        async with pool.acquire() as conn:
            row = await conn.fetchrow(
                """
                SELECT user_id FROM user_sessions
                WHERE token_hash = $1
                  AND revoked_at IS NULL
                  AND expires_at > NOW()
                """,
                token_hash,
            )
        return None if row is None else row["user_id"]

    async def revoke_session(self, token_hash: str) -> None:
        pool = await get_pool()
        async with pool.acquire() as conn:
            await conn.execute(
                """
                UPDATE user_sessions
                SET revoked_at = NOW()
                WHERE token_hash = $1 AND revoked_at IS NULL
                """,
                token_hash,
            )
