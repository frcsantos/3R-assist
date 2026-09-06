"""DocumentRepository — catalogue of source documents."""

from __future__ import annotations

import json

from app.db.connection import get_pool
from app.models.document import Document
from app.models.i18n import parse_localized_str


def _parse_categories(value) -> list[str]:
    if value is None:
        return []
    if isinstance(value, str):
        value = json.loads(value) if value.strip() else []
    if isinstance(value, list):
        return [str(item) for item in value if item is not None and str(item).strip()]
    return []


class DocumentRepository:
    _SELECT_COLUMNS = """
        d.id, d.slug, d.doc_citation, d.description, d."date",
        d.categories, d.institution, d.url
    """

    async def list_all(
        self,
        *,
        categories: list[str] | None = None,
    ) -> list[Document]:
        pool = await get_pool()
        async with pool.acquire() as conn:
            if categories:
                rows = await conn.fetch(
                    f"""
                    SELECT {self._SELECT_COLUMNS}
                    FROM documents d
                    WHERE d.categories ?| $1::text[]
                    ORDER BY d.doc_citation->>'en-us', d.slug
                    """,
                    categories,
                )
            else:
                rows = await conn.fetch(
                    f"""
                    SELECT {self._SELECT_COLUMNS}
                    FROM documents d
                    ORDER BY d.doc_citation->>'en-us', d.slug
                    """
                )
        return [self._row_to_document(row) for row in rows]

    @staticmethod
    def _row_to_document(row) -> Document:
        return Document(
            id=row["id"],
            slug=row["slug"],
            doc_citation=parse_localized_str(row["doc_citation"]),
            description=parse_localized_str(row["description"], required=False),
            date=row["date"],
            categories=_parse_categories(row["categories"]),
            institution=parse_localized_str(row["institution"], required=False),
            url=row["url"],
        )
