"""CLI script: download PubMed baseline from NCBI FTP and ingest into the DB.

Each record produces two embeddings:
  endpoint_embedding  — title + background/objective text (drives Path A search)
  method_embedding    — methods/results text (drives Path B search)

Usage:
    # Full baseline (~1100 files, ~37M records total):
    python scripts/run_pubmed_ingestion.py

    # Test run — first 5 files only:
    python scripts/run_pubmed_ingestion.py --max-files 5

    # Use already-downloaded files (skip FTP):
    python scripts/run_pubmed_ingestion.py --local-dir /data/pubmed --skip-download

After loading > 10 000 records, create the vector indexes in PostgreSQL:

    CREATE INDEX pubmed_endpoint_embedding_idx ON pubmed_abstracts
      USING ivfflat (endpoint_embedding vector_cosine_ops) WITH (lists = 1000);

    CREATE INDEX pubmed_method_embedding_idx ON pubmed_abstracts
      USING ivfflat (method_embedding vector_cosine_ops) WITH (lists = 1000);
"""

from __future__ import annotations

import argparse
import asyncio
import logging
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from app.adapters.embedder import SentenceTransformerEmbedder
from app.config import get_settings
from app.db.connection import create_pool
from pubmed.db.repository import PubMedRepository
from pubmed.ingestion.pipeline import run_baseline

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(name)s: %(message)s",
)
logger = logging.getLogger("pubmed_ingestion")


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

    dest_dir = Path(args.local_dir) if args.local_dir else Path("data/pubmed_baseline")

    await run_baseline(
        dest_dir=dest_dir,
        repository=repository,
        embedder=embedder,
        max_files=args.max_files,
        skip_download=args.skip_download,
    )

    after = await repository.count()
    logger.info(
        "Done. Records: %d → %d (+%d)",
        before, after, after - before,
    )
    if after > 10_000:
        logger.info(
            "Index tip: run the two IVFFlat CREATE INDEX statements now "
            "(see script docstring) to enable fast approximate search."
        )


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Ingest PubMed baseline into pgvector DB")
    parser.add_argument("--max-files", type=int, default=None)
    parser.add_argument("--local-dir", type=str, default=None)
    parser.add_argument("--skip-download", action="store_true")
    asyncio.run(main(parser.parse_args()))
