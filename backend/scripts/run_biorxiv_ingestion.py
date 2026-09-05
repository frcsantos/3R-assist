"""Ingest bioRxiv preprints into the pubmed_abstracts table.

Deduplication: preprints whose published DOI is already in the DB (from PubMed)
are skipped automatically. Re-running is safe — existing records are upserted.

Usage:
    # Full dataset from bioRxiv launch to today:
    python scripts/run_biorxiv_ingestion.py

    # Custom date range:
    python scripts/run_biorxiv_ingestion.py --start 2020-01-01 --end 2024-12-31

Before running, apply the migration if you haven't already:
    psql $DATABASE_URL -f app/db/migrations/010_add_doi_source.sql
"""

from __future__ import annotations

import argparse
import asyncio
import logging
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import asyncpg
from app.adapters.embedder import SentenceTransformerEmbedder
from app.config import get_settings
from app.db.connection import create_pool, get_pool
from pubmed.db.repository import PubMedRepository
from pubmed.ingestion.biorxiv_pipeline import run_biorxiv

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(name)s: %(message)s",
)
logger = logging.getLogger("biorxiv_ingestion")


async def main(args: argparse.Namespace) -> None:
    settings = get_settings()
    if not settings.database_url:
        logger.error("DATABASE_URL is not set.")
        sys.exit(1)

    logger.info("Connecting to database...")
    await create_pool()

    logger.info("Loading embedding model: %s", settings.embedding_model)
    embedder = SentenceTransformerEmbedder(settings.embedding_model)

    repository = PubMedRepository()
    before = await repository.count()
    logger.info("Records in DB before ingestion: %d", before)

    inserted = await run_biorxiv(
        repository=repository,
        embedder=embedder,
        start_date=args.start,
        end_date=args.end,
    )

    after = await repository.count()
    logger.info("Done. Records: %d → %d (+%d inserted)", before, after, inserted)

    # Remove bioRxiv preprints superseded by their published PubMed version
    logger.info("Deduplicating: removing bioRxiv records whose journal version is in PubMed...")
    pool = await get_pool()
    async with pool.acquire() as conn:
        deleted = await conn.fetchval("""
            WITH to_delete AS (
                SELECT b.pmid FROM pubmed_abstracts b
                JOIN pubmed_abstracts p ON p.doi = b.published_doi
                WHERE b.source = 'biorxiv'
                  AND b.published_doi IS NOT NULL
                  AND p.source = 'pubmed'
            )
            DELETE FROM pubmed_abstracts
            WHERE pmid IN (SELECT pmid FROM to_delete)
            RETURNING 1
        """)
    logger.info("Deduplication done. Removed %d records.", deleted or 0)

    # Rebuild HNSW indexes in parallel — each in its own connection with no timeout
    logger.info("Rebuilding HNSW indexes in parallel — this will take several hours...")
    pool = await get_pool()
    async with pool.acquire() as conn:
        try:
            await conn.execute("ALTER SYSTEM SET max_parallel_workers = 16")
            await conn.execute("SELECT pg_reload_conf()")
            logger.info("Set max_parallel_workers = 16")
        except Exception as exc:
            logger.warning("Could not set max_parallel_workers: %s", exc)

    async def build_index(name: str, column: str) -> None:
        conn = await asyncpg.connect(settings.database_url, command_timeout=None)
        try:
            await conn.execute("SET maintenance_work_mem = '12GB'")
            await conn.execute("SET max_parallel_maintenance_workers = 8")
            logger.info("Building %s...", name)
            await conn.execute(f"""
                CREATE INDEX IF NOT EXISTS {name}
                ON pubmed_abstracts
                USING hnsw ({column} vector_cosine_ops)
                WITH (m = 16, ef_construction = 64)
            """)
            logger.info("%s done.", name)
        finally:
            await conn.close()

    await asyncio.gather(
        build_index("pubmed_endpoint_embedding_idx", "endpoint_embedding"),
        build_index("pubmed_method_embedding_idx",  "method_embedding"),
    )
    logger.info("HNSW indexes built. Part 2 search is now fully operational.")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Ingest bioRxiv preprints into the DB")
    parser.add_argument("--start", default="2013-11-01", help="Start date YYYY-MM-DD")
    parser.add_argument("--end", default=None, help="End date YYYY-MM-DD (default: today)")
    asyncio.run(main(parser.parse_args()))
