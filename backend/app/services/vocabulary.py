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
from typing import Literal

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


@dataclass(frozen=True)
class EndpointRow:
    id: int
    slug: str
    parent_slug: str | None
    code: str
    name: dict


_applications: dict[str, ApplicationRow] = {}
_loaded_at: float = 0.0

# Slug lists of the simple vocabularies, keyed by table name.
_SLUG_TABLES = ("routes", "species")
_slugs: dict[str, tuple[str, ...]] = {}
# Endpoint tree (endpoints.parent_id), keyed by slug in display order.
_endpoint_rows: dict[str, EndpointRow] = {}


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
    _endpoint_rows.clear()


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


def set_endpoint_rows(rows: list[EndpointRow]) -> None:
    """Replace the cached endpoint tree and slug list (also used by tests)."""
    _endpoint_rows.clear()
    _endpoint_rows.update({row.slug: row for row in rows})
    _slugs["endpoints"] = tuple(_endpoint_rows)


def endpoint_rows() -> list[EndpointRow]:
    return list(_endpoint_rows.values())


def endpoint_ancestors(slug: str) -> list[str]:
    """Slugs from the parent up to the root (nearest first); empty if unknown."""
    ancestors: list[str] = []
    row = _endpoint_rows.get(slug)
    while row is not None and row.parent_slug and row.parent_slug not in ancestors:
        ancestors.append(row.parent_slug)
        row = _endpoint_rows.get(row.parent_slug)
    return ancestors


EndpointRelation = Literal["exact", "specific", "general"]


def endpoint_relation(wanted: str, method_slugs: set[str]) -> EndpointRelation | None:
    """How a method's endpoints relate to the protocol's endpoint.

    exact:    the method lists the endpoint itself.
    specific: the method lists a descendant (a narrower test of the same group).
    general:  the method lists a non-root ancestor (a broader test that covers it).
    Without the tree loaded (tests, database unavailable) only exact matches count.
    """
    if wanted in method_slugs:
        return "exact"
    if any(wanted in endpoint_ancestors(slug) for slug in method_slugs):
        return "specific"
    # The root (e.g. "human-health-effects") is too broad to count as coverage.
    if any(
        ancestor in method_slugs and endpoint_ancestors(ancestor)
        for ancestor in endpoint_ancestors(wanted)
    ):
        return "general"
    return None


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
        endpoints = await conn.fetch(
            "SELECT e.id, e.slug, p.slug AS parent_slug, e.code, e.name "
            "FROM endpoints e LEFT JOIN endpoints p ON p.id = e.parent_id "
            "WHERE e.active ORDER BY e.sort_order, e.id"
        )
    if endpoints:
        set_endpoint_rows(
            [
                EndpointRow(
                    id=int(r["id"]),
                    slug=r["slug"],
                    parent_slug=r["parent_slug"],
                    code=r["code"] or "",
                    name=_localized(r["name"]),
                )
                for r in endpoints
            ]
        )


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


def endpoint_prompt_lines() -> str:
    """One indented `slug: name` line per endpoint (tree order), for LLM prompts."""
    rows = endpoint_rows()
    if not rows:
        return ""
    lines = []
    for row in rows:
        depth = len(endpoint_ancestors(row.slug))
        label = row.name.get("en-us") or row.slug
        lines.append(f"{'  ' * (depth + 1)}{row.slug}: {label}")
    return "\n".join(lines)
