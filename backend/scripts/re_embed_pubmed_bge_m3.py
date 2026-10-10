#!/usr/bin/env python3
"""
re_embed_pubmed_bge_m3.py — Fill endpoint_embedding_v2 / method_embedding_v2
using BAAI/bge-m3 (1024 dims) via PyTorch MPS (Apple Silicon GPU).

Optimisations:
  - float16 on MPS (~2x faster than float32)
  - Combined endpoint+method encode in one model.encode() call
  - Binary pgvector codec (4 kB/vector vs 18 kB text; no PostgreSQL text parsing)
  - Pipeline: DB write overlaps with next-batch embedding (ThreadPoolExecutor)
  - Cursor-based DB fetch (primary-key index, no full-table scan per batch)

Resumable: progress saved to /tmp/re_embed_bge_m3_cursor.txt.
Interrupt safely with Ctrl-C or Cmd-Z + kill %1 at any time.

Usage:
    python scripts/re_embed_pubmed_bge_m3.py            # resume / start
    python scripts/re_embed_pubmed_bge_m3.py --reset    # start from pmid 0
    python scripts/re_embed_pubmed_bge_m3.py --dry-run  # counts only, no writes
"""

from __future__ import annotations

import argparse
import asyncio
import concurrent.futures
import logging
import os
import struct
import sys
import time
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s: %(message)s",
)
logger = logging.getLogger("re_embed")

MODEL_NAME    = "BAAI/bge-m3"
DEFAULT_BATCH = 1024        # DB records per round-trip
CURSOR_FILE   = Path("/tmp/re_embed_bge_m3_cursor.txt")
_TIMING_BATCHES = 5         # show embed/write split for first N batches


# ── Binary pgvector codec ─────────────────────────────────────────────────────
# Wire format: int16 dim | int16 unused(0) | dim × float32  (big-endian)
# 1024 dims = 4 100 bytes vs ~18 KB text — 4.5× smaller, no PostgreSQL parsing.
#
# asyncpg auto-detects numpy arrays as multi-dimensional and bypasses custom
# codecs, so we pre-encode to plain Python bytes in embed_records().
# asyncpg does NOT flag list[bytes] as nested arrays, so the codec fires and
# passes bytes straight through to PostgreSQL's vector_recv().

def _vec_to_bytes(arr) -> bytes:
    a = np.asarray(arr, dtype=np.float32)
    return struct.pack('>hh', len(a), 0) + a.astype('>f4').tobytes()


def _vec_codec_encode(obj) -> bytes:
    if isinstance(obj, (bytes, bytearray, memoryview)):
        return bytes(obj)
    return _vec_to_bytes(obj)


def _vec_codec_decode(data: bytes):
    n = struct.unpack_from('>h', data)[0]
    return np.frombuffer(data, dtype='>f4', count=n, offset=4)


async def register_vector_codec(conn) -> None:
    await conn.set_type_codec(
        'vector',
        schema='public',
        encoder=_vec_codec_encode,
        decoder=_vec_codec_decode,
        format='binary',
    )


# ── Model ─────────────────────────────────────────────────────────────────────

def load_model(device: str | None = None):
    try:
        import torch
        from sentence_transformers import SentenceTransformer
    except ImportError:
        logger.error("pip install sentence-transformers torch")
        sys.exit(1)

    torch.set_num_threads(os.cpu_count() or 4)

    if device is None:
        if torch.backends.mps.is_available():
            device = "mps"
        elif torch.cuda.is_available():
            device = "cuda"
        else:
            device = "cpu"

    logger.info("Loading %s on %s ...", MODEL_NAME, device)
    model = SentenceTransformer(MODEL_NAME, device=device)

    if device in ("mps", "cuda"):
        try:
            model.half()
            logger.info("float16 enabled.")
        except Exception as e:
            logger.warning("float16 failed (%s), continuing float32.", e)

    model.max_seq_length = 512
    logger.info("max_seq_length: %d tokens", model.max_seq_length)
    return model


def embed_records(model, rows: list[dict]) -> tuple[list[str], list[bytes], list[bytes]]:
    """
    Encode endpoint + method texts in one combined model.encode() call.
    Returns (pmids, ep_bytes, meth_bytes) pre-encoded to pgvector binary.
    """
    n = len(rows)
    all_texts = (
        [f"{r['title']}. {r['endpoint_text']}" for r in rows]
        + [r["method_text"] for r in rows]
    )

    vecs = model.encode(all_texts, normalize_embeddings=True, show_progress_bar=False, batch_size=256)

    pmids      = [r["pmid"] for r in rows]
    ep_bytes   = [_vec_to_bytes(vecs[i])     for i in range(n)]
    meth_bytes = [_vec_to_bytes(vecs[i + n]) for i in range(n)]

    return pmids, ep_bytes, meth_bytes


# ── Database ──────────────────────────────────────────────────────────────────

async def connect(database_url: str):
    try:
        import asyncpg
    except ImportError:
        logger.error("asyncpg not installed.")
        sys.exit(1)
    try:
        conn = await asyncpg.connect(database_url)
        await register_vector_codec(conn)
        return conn
    except Exception as e:
        logger.error("DB connection failed: %s", e)
        sys.exit(1)


async def fetch_batch(conn, cursor_pmid: str, batch_size: int) -> list[dict]:
    rows = await conn.fetch(
        """
        SELECT pmid, title, endpoint_text, method_text
          FROM pubmed_abstracts
         WHERE pmid > $1
           AND endpoint_embedding_v2 IS NULL
         ORDER BY pmid
         LIMIT $2
        """,
        cursor_pmid, batch_size,
    )
    return [dict(r) for r in rows]


async def save_batch(conn, pmids: list[str], ep_bytes: list[bytes], meth_bytes: list[bytes]) -> None:
    """Single UPDATE FROM unnest() — one DB round-trip, binary-encoded vectors."""
    await conn.execute(
        """
        UPDATE pubmed_abstracts pa
           SET endpoint_embedding_v2 = d.ep,
               method_embedding_v2   = d.meth
          FROM unnest($1::text[], $2::vector[], $3::vector[]) AS d(pmid, ep, meth)
         WHERE pa.pmid = d.pmid
        """,
        pmids, ep_bytes, meth_bytes,
    )


# ── Cursor ────────────────────────────────────────────────────────────────────

def load_cursor() -> str:
    if CURSOR_FILE.exists():
        cursor = CURSOR_FILE.read_text().strip()
        logger.info("Resuming from cursor pmid: %s", cursor)
        return cursor
    return ""


def save_cursor(pmid: str) -> None:
    CURSOR_FILE.write_text(pmid)


# ── Main loop ─────────────────────────────────────────────────────────────────

async def run(database_url: str, batch_size: int, dry_run: bool, reset: bool, device: str | None = None, sleep: float = 0.0) -> None:
    conn = await connect(database_url)
    try:
        total     = await conn.fetchval("SELECT COUNT(*) FROM pubmed_abstracts")
        remaining = await conn.fetchval(
            "SELECT COUNT(*) FROM pubmed_abstracts WHERE endpoint_embedding_v2 IS NULL"
        )
        done = total - remaining

        logger.info("Total:            %d", total)
        logger.info("Already embedded: %d  (%.1f%%)", done, 100 * done / total if total else 0)
        logger.info("Remaining:        %d", remaining)

        if dry_run:
            logger.info("Dry run — exiting without changes.")
            return

        if remaining == 0:
            logger.info("Nothing to do.")
            CURSOR_FILE.unlink(missing_ok=True)
            return

        if reset:
            CURSOR_FILE.unlink(missing_ok=True)
            logger.info("Cursor reset — starting from the beginning.")

        cursor_pmid = load_cursor()
        model       = load_model(device)

        rows = await fetch_batch(conn, cursor_pmid, batch_size)
        if not rows:
            logger.info("No records found after cursor.")
            return

        executor  = concurrent.futures.ThreadPoolExecutor(max_workers=1)
        loop      = asyncio.get_event_loop()
        start     = time.monotonic()
        processed = 0
        batch_num = 0

        embed_t0  = time.monotonic()
        embed_fut = loop.run_in_executor(executor, embed_records, model, rows)

        while True:
            fetch_task = asyncio.create_task(fetch_batch(conn, rows[-1]["pmid"], batch_size))

            pmids, ep_bytes, meth_bytes = await embed_fut
            embed_elapsed = time.monotonic() - embed_t0

            next_rows = await fetch_task

            write_t0   = time.monotonic()
            write_task = asyncio.create_task(save_batch(conn, pmids, ep_bytes, meth_bytes))

            if next_rows:
                embed_t0  = time.monotonic()
                embed_fut = loop.run_in_executor(executor, embed_records, model, next_rows)

            await write_task
            write_elapsed = time.monotonic() - write_t0

            save_cursor(rows[-1]["pmid"])
            processed += len(rows)
            batch_num += 1

            elapsed = time.monotonic() - start
            rate    = processed / elapsed if elapsed > 0 else 0
            eta_h   = (remaining - processed) / rate / 3600 if rate > 0 else float("inf")

            if batch_num <= _TIMING_BATCHES:
                logger.info(
                    "  %d / %d  (%.1f%%)  |  %.0f rec/s  |  ETA %.1fh"
                    "  [embed %.2fs  write %.2fs]",
                    done + processed, total,
                    100 * (done + processed) / total,
                    rate, eta_h,
                    embed_elapsed, write_elapsed,
                )
            else:
                logger.info(
                    "  %d / %d  (%.1f%%)  |  %.0f rec/s  |  ETA %.1fh",
                    done + processed, total,
                    100 * (done + processed) / total,
                    rate, eta_h,
                )

            if not next_rows:
                break

            if sleep > 0:
                await asyncio.sleep(sleep)

            rows = next_rows

        CURSOR_FILE.unlink(missing_ok=True)
        elapsed = time.monotonic() - start
        logger.info(
            "Done. %d records in %.1fh  (%.0f rec/s).",
            processed, elapsed / 3600,
            processed / elapsed if elapsed > 0 else 0,
        )

    finally:
        await conn.close()


def main() -> None:
    try:
        from dotenv import load_dotenv
        backend_dir = Path(__file__).resolve().parents[1]
        load_dotenv(backend_dir / ".env")
        load_dotenv(backend_dir.parent / ".env")
    except ImportError:
        pass

    parser = argparse.ArgumentParser(
        description="Re-embed pubmed_abstracts using BAAI/bge-m3 via PyTorch MPS."
    )
    parser.add_argument("--batch-size", type=int, default=DEFAULT_BATCH,
                        help="DB records per batch (default: %(default)s)")
    parser.add_argument("--dry-run", action="store_true",
                        help="Print counts only, no DB writes.")
    parser.add_argument("--reset", action="store_true",
                        help="Ignore saved cursor and start from pmid 0.")
    parser.add_argument("--device", default=None,
                        help="Force device: cpu, mps, cuda (default: auto-detect).")
    parser.add_argument("--sleep", type=float, default=0.0,
                        help="Seconds to sleep between batches (throttle for daytime use).")
    args = parser.parse_args()

    database_url = os.environ.get("DATABASE_URL")
    if not database_url:
        logger.error("DATABASE_URL not set.")
        sys.exit(1)

    asyncio.run(run(database_url, args.batch_size, args.dry_run, args.reset, args.device, args.sleep))


if __name__ == "__main__":
    main()
