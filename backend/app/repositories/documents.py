"""DocumentRepository — catalogue of source documents."""

from __future__ import annotations

from app.db.connection import get_pool
from app.models.document import Document
from app.models.i18n import parse_localized_str


class DocumentRepository:
    _SELECT_COLUMNS = """
        d.id, d.slug, d.doc_citation, d.description, d."date", d.category, d.url
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
                    WHERE d.category = ANY($1::text[])
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
            category=row["category"],
            url=row["url"],
        )
