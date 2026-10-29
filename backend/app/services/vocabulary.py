"""Controlled vocabularies that live in database tables.

The `applications`, `routes`, `species` and `endpoints` tables are the source
of truth for the allowed slugs. This module keeps a short-lived in-process copy so that synchronous code
(pydantic validators, prompt builders) can read it. Nothing here lists
individual categories: the only literals are the default/fallback slug and
the species markers that are not organisms (`SPECIES_MARKERS`).
"""

from __future__ import annotations

import logging
import time
from dataclasses import dataclass

from app.config import get_settings

logger = logging.getLogger(__name__)

DEFAULT_APPLICATION = "basic-research"
# Values the extraction may return for `species` that are not rows of `species`.
SPECIES_MARKERS = ("in_vitro", "other")
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

# Slug lists of the simple vocabularies, keyed by table name.
_SLUG_TABLES = ("routes", "species", "endpoints")
_slugs: dict[str, tuple[str, ...]] = {}


def set_applications(rows: list[ApplicationRow]) -> None:
    """Replace the cached applications (also used by tests)."""
    global _applications, _loaded_at
    _applications = {row.slug: row for row in sorted(rows, key=lambda r: (r.sort_order, r.id))}
    _loaded_at = time.monotonic()


def clear_applications() -> None:
    global _applications, _loaded_at
    _applications = {}
    _loaded_at = 0.0
    _slugs.clear()


def set_slugs(table: str, slugs: list[str]) -> None:
    """Replace the cached slugs of `routes`, `species` or `endpoints` (also used by tests)."""
    _slugs[table] = tuple(slugs)


def slugs_loaded(table: str) -> bool:
    return bool(_slugs.get(table))


def route_slugs() -> tuple[str, ...]:
    return _slugs.get("routes", ())


def species_slugs() -> tuple[str, ...]:
    """Species rows plus the non-organism markers (`in_vitro`, `other`)."""
    rows = _slugs.get("species", ())
    return rows + tuple(m for m in SPECIES_MARKERS if m not in rows) if rows else ()


def endpoint_slugs() -> tuple[str, ...]:
    return _slugs.get("endpoints", ())


async def load_slug_vocabularies() -> None:
    from app.db.connection import get_pool

    pool = await get_pool()
    async with pool.acquire() as conn:
        for table in _SLUG_TABLES:
            records = await conn.fetch(
                f"SELECT slug FROM {table} WHERE active ORDER BY sort_order, id"
            )
            if records:
                set_slugs(table, [r["slug"] for r in records])


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
        await load_slug_vocabularies()
    except Exception as exc:  # DB unavailable: keep stale cache or fallback
        logger.warning("Could not load vocabularies: %s", exc)


def application_prompt_lines() -> str:
    """One `slug: description` line per application, for LLM prompts."""
    rows = application_rows()
    if not rows:
        return DEFAULT_APPLICATION
    return "\n".join(
        f"  {row.slug}: {row.description.get('en-us') or row.name.get('en-us') or row.slug}"
        for row in rows
    )
