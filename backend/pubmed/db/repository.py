from __future__ import annotations

import json

from app.db.connection import get_pool
from pubmed.models.record import Author, PubMedRecord

# ── Vector search queries ────────────────────────────────────────────────────

_SEARCH_ENDPOINT = """
    SELECT
        pmid, title, authors, institutions,
        pub_year, pub_month, journal,
        abstract_text, endpoint_text, method_text, mesh_terms, cluster,
        1 - (endpoint_embedding <=> $1::vector) AS score
    FROM pubmed_abstracts
    WHERE endpoint_embedding IS NOT NULL
    ORDER BY endpoint_embedding <=> $1::vector
    LIMIT $2
"""

_SEARCH_METHOD = """
    SELECT
        pmid, title, authors, institutions,
        pub_year, pub_month, journal,
        abstract_text, endpoint_text, method_text, mesh_terms, cluster,
        1 - (method_embedding <=> $1::vector) AS score
    FROM pubmed_abstracts
    WHERE method_embedding IS NOT NULL
    ORDER BY method_embedding <=> $1::vector
    LIMIT $2
"""

# ── Insert / upsert ──────────────────────────────────────────────────────────

_INSERT_RECORD = """
    INSERT INTO pubmed_abstracts (
        pmid, title, authors, institutions,
        pub_year, pub_month, journal,
        abstract_text, endpoint_text, method_text, mesh_terms, cluster,
        endpoint_embedding, method_embedding
    )
    VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9, $10, $11, $12, $13::vector, $14::vector)
    ON CONFLICT (pmid) DO UPDATE SET
        title               = EXCLUDED.title,
        authors             = EXCLUDED.authors,
        institutions        = EXCLUDED.institutions,
        pub_year            = EXCLUDED.pub_year,
        pub_month           = EXCLUDED.pub_month,
        journal             = EXCLUDED.journal,
        abstract_text       = EXCLUDED.abstract_text,
        endpoint_text       = EXCLUDED.endpoint_text,
        method_text         = EXCLUDED.method_text,
        mesh_terms          = EXCLUDED.mesh_terms,
        cluster             = EXCLUDED.cluster,
        endpoint_embedding  = EXCLUDED.endpoint_embedding,
        method_embedding    = EXCLUDED.method_embedding,
        indexed_at          = NOW()
"""

_COUNT_RECORDS = "SELECT COUNT(*) FROM pubmed_abstracts"

_CREATE_INGESTED_FILES_TABLE = """
    CREATE TABLE IF NOT EXISTS pubmed_ingested_files (
        filename   TEXT        PRIMARY KEY,
        ingested_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
    )
"""
_FILE_INGESTED = "SELECT 1 FROM pubmed_ingested_files WHERE filename = $1"
_MARK_FILE_INGESTED = """
    INSERT INTO pubmed_ingested_files (filename)
    VALUES ($1)
    ON CONFLICT (filename) DO NOTHING
"""


def _vec_str(embedding: list[float]) -> str:
    return "[" + ",".join(str(v) for v in embedding) + "]"


class PubMedRepository:
    async def search_by_endpoint_embedding(
        self,
        embedding: list[float],
        *,
        top_k: int = 12,
    ) -> list[tuple[PubMedRecord, float]]:
        """Path A: search by endpoint/hypothesis embedding."""
        pool = await get_pool()
        async with pool.acquire() as conn:
            rows = await conn.fetch(_SEARCH_ENDPOINT, _vec_str(embedding), top_k)
        return [(self._row_to_record(row), float(row["score"])) for row in rows]

    async def search_by_method_embedding(
        self,
        embedding: list[float],
        *,
        top_k: int = 15,
    ) -> list[tuple[PubMedRecord, float]]:
        """Path B: search by method/technique embedding."""
        pool = await get_pool()
        async with pool.acquire() as conn:
            rows = await conn.fetch(_SEARCH_METHOD, _vec_str(embedding), top_k)
        return [(self._row_to_record(row), float(row["score"])) for row in rows]

    async def insert_batch(
        self,
        records: list[PubMedRecord],
        endpoint_embeddings: list[list[float]],
        method_embeddings: list[list[float]],
    ) -> int:
        pool = await get_pool()
        count = 0
        async with pool.acquire() as conn:
            async with conn.transaction():
                for record, ep_emb, meth_emb in zip(
                    records, endpoint_embeddings, method_embeddings, strict=True
                ):
                    await conn.execute(
                        _INSERT_RECORD,
                        record.pmid,
                        record.title,
                        json.dumps([a.model_dump() for a in record.authors]),
                        json.dumps(record.institutions),
                        record.pub_year,
                        record.pub_month,
                        record.journal,
                        record.abstract_text,
                        record.endpoint_text,
                        record.method_text,
                        json.dumps(record.mesh_terms),
                        record.cluster,
                        _vec_str(ep_emb),
                        _vec_str(meth_emb),
                    )
                    count += 1
        return count

    async def count(self) -> int:
        pool = await get_pool()
        async with pool.acquire() as conn:
            return await conn.fetchval(_COUNT_RECORDS)

    async def ensure_ingestion_table(self) -> None:
        pool = await get_pool()
        async with pool.acquire() as conn:
            await conn.execute(_CREATE_INGESTED_FILES_TABLE)

    async def is_file_ingested(self, filename: str) -> bool:
        pool = await get_pool()
        async with pool.acquire() as conn:
            row = await conn.fetchrow(_FILE_INGESTED, filename)
            return row is not None

    async def mark_file_ingested(self, filename: str) -> None:
        pool = await get_pool()
        async with pool.acquire() as conn:
            await conn.execute(_MARK_FILE_INGESTED, filename)

    @staticmethod
    def _row_to_record(row) -> PubMedRecord:
        def _load(val):
            return val if isinstance(val, list) else json.loads(val)

        return PubMedRecord(
            pmid=row["pmid"],
            title=row["title"],
            authors=[Author.model_validate(a) for a in _load(row["authors"])],
            institutions=_load(row["institutions"]),
            pub_year=row["pub_year"],
            pub_month=row["pub_month"],
            journal=row["journal"],
            abstract_text=row["abstract_text"],
            endpoint_text=row["endpoint_text"],
            method_text=row["method_text"],
            mesh_terms=_load(row["mesh_terms"]),
            cluster=row["cluster"],
        )
