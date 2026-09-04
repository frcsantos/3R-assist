"""Ingestion pipeline: FTP download → parse → embed (×2) → insert."""

from __future__ import annotations

import asyncio
import ftplib
import gzip
import logging
from pathlib import Path

from app.adapters.embedder import EmbedderAdapter
from pubmed.db.repository import PubMedRepository
from pubmed.ingestion import ftp as ftp_module
from pubmed.ingestion.parser import parse_file
from pubmed.models.record import PubMedRecord

logger = logging.getLogger(__name__)

EMBED_BATCH_SIZE = 128
INSERT_BATCH_SIZE = 256


def _embed_record_batch(
    records: list[PubMedRecord],
    embedder: EmbedderAdapter,
) -> tuple[list[list[float]], list[list[float]]]:
    """Return (endpoint_embeddings, method_embeddings) for a batch of records."""
    endpoint_texts = [r.to_endpoint_embedding_text() for r in records]
    method_texts = [r.to_method_embedding_text() for r in records]
    endpoint_embeddings = embedder.embed_batch(endpoint_texts)
    method_embeddings = embedder.embed_batch(method_texts)
    return endpoint_embeddings, method_embeddings


async def ingest_file(
    path: Path,
    repository: PubMedRepository,
    embedder: EmbedderAdapter,
) -> dict[str, int]:
    parsed = 0
    inserted = 0
    buffer: list[PubMedRecord] = []

    async def flush(batch: list[PubMedRecord]) -> int:
        ep_embs, meth_embs = await asyncio.get_event_loop().run_in_executor(
            None, _embed_record_batch, batch, embedder
        )
        return await repository.insert_batch(batch, ep_embs, meth_embs)

    for record in parse_file(path):
        buffer.append(record)
        parsed += 1
        if len(buffer) >= INSERT_BATCH_SIZE:
            inserted += await flush(buffer)
            buffer.clear()
            logger.info("  %s — inserted %d so far", path.name, inserted)

    if buffer:
        inserted += await flush(buffer)

    return {"parsed": parsed, "inserted": inserted}


_MAX_RETRIES = 5


def _is_valid_gz(path: Path) -> bool:
    """Return False if the file is missing, empty, or not a valid gzip stream."""
    if not path.exists() or path.stat().st_size == 0:
        return False
    try:
        with gzip.open(path, "rb") as fh:
            fh.read(16)
        return True
    except Exception:
        return False


def _reconnect(ftp: ftplib.FTP | None) -> ftplib.FTP:
    try:
        if ftp is not None:
            ftp.quit()
    except Exception:
        pass
    return ftp_module.connect()


async def run_baseline(
    dest_dir: Path,
    repository: PubMedRepository,
    embedder: EmbedderAdapter,
    *,
    max_files: int | None = None,
    skip_download: bool = False,
) -> None:
    dest_dir.mkdir(parents=True, exist_ok=True)
    await repository.ensure_ingestion_table()

    ftp = ftp_module.connect()
    files = ftp_module.list_baseline_files(ftp)
    if max_files:
        files = files[:max_files]

    logger.info("Baseline: %d files to process", len(files))

    for filename in files:
        if await repository.is_file_ingested(filename):
            logger.info("Already ingested, skipping: %s", filename)
            continue

        local_path = dest_dir / filename

        if not skip_download:
            for attempt in range(1, _MAX_RETRIES + 1):
                try:
                    local_path = ftp_module.download_file(
                        ftp, filename, dest_dir, verify=True
                    )
                    break
                except Exception as exc:
                    logger.warning(
                        "Download failed for %s (attempt %d/%d): %s",
                        filename, attempt, _MAX_RETRIES, exc,
                    )
                    ftp = _reconnect(ftp)
                    (dest_dir / filename).unlink(missing_ok=True)
                    if attempt == _MAX_RETRIES:
                        logger.error("Giving up on %s after %d attempts", filename, _MAX_RETRIES)
                        local_path = None

        if local_path is None or not local_path.exists():
            logger.warning("Skipping missing file: %s", filename)
            continue

        logger.info("Processing %s ...", filename)
        stats = await ingest_file(local_path, repository, embedder)
        await repository.mark_file_ingested(filename)
        logger.info(
            "  %s — parsed=%d inserted=%d",
            filename,
            stats["parsed"],
            stats["inserted"],
        )
