"""Ingestion pipeline: FTP download → parse → embed (×2) → insert."""

from __future__ import annotations

import asyncio
import ftplib
import gzip
import logging
import os
from pathlib import Path

import torch

from app.adapters.embedder import EmbedderAdapter
from pubmed.db.repository import PubMedRepository
from pubmed.ingestion import ftp as ftp_module
from pubmed.ingestion.parser import parse_file
from pubmed.models.record import PubMedRecord

logger = logging.getLogger(__name__)

# Use all CPU cores for torch tokenization
_CPU_CORES = os.cpu_count() or 4
torch.set_num_threads(_CPU_CORES)

EMBED_BATCH_SIZE = 1024
INSERT_BATCH_SIZE = 1024


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


def _parse_file_to_list(path: Path) -> list[PubMedRecord]:
    return list(parse_file(path))


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

    if skip_download:
        all_files = sorted(dest_dir.glob("pubmed*.xml.gz"))
        filenames = [p.name for p in all_files]
    else:
        ftp = ftp_module.connect()
        filenames = ftp_module.list_baseline_files(ftp)

    if max_files:
        filenames = filenames[:max_files]

    logger.info("Baseline: %d files to process", len(filenames))
    logger.info("Using %d CPU threads for tokenization", _CPU_CORES)

    ftp = None if skip_download else ftp_module.connect()
    loop = asyncio.get_event_loop()

    # Build list of pending paths
    pending: list[Path] = []
    for filename in filenames:
        if not await repository.is_file_ingested(filename):
            pending.append(dest_dir / filename)
        else:
            logger.info("Already ingested, skipping: %s", filename)

    if not pending:
        return

    # Pre-parse first file in background
    prefetch = loop.run_in_executor(None, _parse_file_to_list, pending[0])

    for i, path in enumerate(pending):
        if not path.exists():
            logger.warning("Skipping missing file: %s", path.name)
            prefetch = loop.run_in_executor(None, _parse_file_to_list, pending[i + 1]) if i + 1 < len(pending) else None
            continue

        # Wait for pre-parsed records
        records = await prefetch

        # Immediately start parsing next file while we embed+insert current
        if i + 1 < len(pending):
            prefetch = loop.run_in_executor(None, _parse_file_to_list, pending[i + 1])

        logger.info("Processing %s (%d records)...", path.name, len(records))
        inserted = 0
        buffer: list[PubMedRecord] = []

        for record in records:
            buffer.append(record)
            if len(buffer) >= INSERT_BATCH_SIZE:
                ep_embs, meth_embs = await loop.run_in_executor(
                    None, _embed_record_batch, buffer, embedder
                )
                inserted += await repository.insert_batch(buffer, ep_embs, meth_embs)
                logger.info("  %s — inserted %d so far", path.name, inserted)
                buffer.clear()

        if buffer:
            ep_embs, meth_embs = await loop.run_in_executor(
                None, _embed_record_batch, buffer, embedder
            )
            inserted += await repository.insert_batch(buffer, ep_embs, meth_embs)

        await repository.mark_file_ingested(path.name)
        logger.info("  %s — done, inserted=%d", path.name, inserted)
