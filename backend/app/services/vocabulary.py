"""Controlled vocabularies that live in database tables.

The `applications` table is the source of truth for the allowed application
slugs. This module keeps a short-lived in-process copy so that synchronous code
(pydantic validators, prompt builders) can read it. Nothing here lists
individual categories: the only literal is the default/fallback slug.
"""

from __future__ import annotations

import logging
import time
from dataclasses import dataclass

from app.config import get_settings

logger = logging.getLogger(__name__)

DEFAULT_APPLICATION = "basic-research"
CACHE_TTL_SECONDS = 60.0


@dataclass(frozen=True)
class ApplicationRow:
    id: int
    slug: str
    name: dict
    description: dict
    sort_order: int


_applications: dict[str, ApplicationRow] = {}
_loaded_at: float = 0.0


def set_applications(rows: list[ApplicationRow]) -> None:
    """Replace the cached applications (also used by tests)."""
    global _applications, _loaded_at
    _applications = {row.slug: row for row in sorted(rows, key=lambda r: (r.sort_order, r.id))}
    _loaded_at = time.monotonic()


def clear_applications() -> None:
    global _applications, _loaded_at
    _applications = {}
    _loaded_at = 0.0


def applications_loaded() -> bool:
    return bool(_applications)


def application_rows() -> list[ApplicationRow]:
    return list(_applications.values())


def application_slugs() -> list[str]:
    """Slugs in display order; falls back to the default slug when not loaded."""
    return list(_applications) or [DEFAULT_APPLICATION]


def _localized(value) -> dict:
    return value if isinstance(value, dict) else {}


async def load_applications() -> list[ApplicationRow]:
    from app.db.connection import get_pool

    pool = await get_pool()
    async with pool.acquire() as conn:
        records = await conn.fetch(
            "SELECT id, slug, name, description, sort_order "
            "FROM applications WHERE active ORDER BY sort_order, id"
        )
    rows = [
        ApplicationRow(
            id=int(r["id"]),
            slug=r["slug"],
            name=_localized(r["name"]),
            description=_localized(r["description"]),
            sort_order=int(r["sort_order"] or 0),
        )
        for r in records
    ]
    if rows:
        set_applications(rows)
    return rows


async def ensure_applications_loaded() -> None:
    """Refresh the cache when empty or older than the TTL. Never raises."""
    if not get_settings().database_url:
        return
    if _applications and (time.monotonic() - _loaded_at) < CACHE_TTL_SECONDS:
        return
    try:
        await load_applications()
    except Exception as exc:  # DB unavailable: keep stale cache or fallback
        logger.warning("Could not load applications vocabulary: %s", exc)


def application_prompt_lines() -> str:
    """One `slug: description` line per application, for LLM prompts."""
    rows = application_rows()
    if not rows:
        return DEFAULT_APPLICATION
    return "\n".join(
        f"  {row.slug}: {row.description.get('en-us') or row.name.get('en-us') or row.slug}"
        for row in rows
    )
