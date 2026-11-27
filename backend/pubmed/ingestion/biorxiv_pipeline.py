"""Fetch bioRxiv preprints via the public API and ingest into pubmed_abstracts.

Deduplication strategy:
  - If a preprint has a published_doi, check if that DOI already exists in the DB
    (meaning the peer-reviewed version is already indexed from PubMed). Skip if so.
  - The bioRxiv DOI (10.1101/...) is stored as both `pmid` and `doi` so the unique
    index on `doi` also blocks re-ingestion of the same preprint across runs.

API endpoint: https://api.biorxiv.org/details/biorxiv/{start}/{end}/{cursor}/json
Returns 100 records per page.
"""

from __future__ import annotations

import asyncio
import logging
import re
import urllib.request
import json as _json
from datetime import date, timedelta

from app.adapters.embedder import SentenceTransformerEmbedder
from pubmed.db.repository import PubMedRepository
from pubmed.ingestion.filters import match_cluster
from pubmed.models.record import Author, PubMedRecord

logger = logging.getLogger(__name__)

_API_BASE = "https://api.biorxiv.org/details/biorxiv"
_API_PAGE_SIZE = 30   # bioRxiv always returns 30 records per page
_BATCH_SIZE = 1024
_CONCURRENCY = 5      # parallel API requests
_CHUNK_DELAY = 0.1    # seconds between parallel chunks

# Labels that map to endpoint context in structured abstracts
_ENDPOINT_LABELS = frozenset({
    "background", "introduction", "objective", "objectives",
    "aim", "aims", "purpose", "conclusion", "conclusions", "summary",
})
_METHOD_LABELS = frozenset({
    "methods", "method", "materials and methods",
    "results", "findings",
})
_SECTION_RE = re.compile(
    r"(?:^|\n)\s*("
    r"background|introduction|objective[s]?|aim[s]?|purpose|"
    r"methods?|materials\s+and\s+methods?|results?|conclusion[s]?|summary"
    r")\s*[:\.\n]",
    re.IGNORECASE,
)


def _split_abstract(abstract: str) -> tuple[str, str]:
    """Return (endpoint_text, method_text). Falls back to full text for both."""
    parts = _SECTION_RE.split(abstract)
    if len(parts) <= 1:
        return abstract, abstract

    endpoint_parts: list[str] = []
    method_parts: list[str] = []
    i = 1
    while i < len(parts) - 1:
        label = parts[i].strip().lower()
        content = parts[i + 1].strip()
        if label in _ENDPOINT_LABELS:
            endpoint_parts.append(content)
        elif label in _METHOD_LABELS:
            method_parts.append(content)
        else:
            endpoint_parts.append(content)
            method_parts.append(content)
        i += 2

    endpoint_text = " ".join(endpoint_parts) if endpoint_parts else abstract
    method_text = " ".join(method_parts) if method_parts else abstract
    return endpoint_text, method_text


def _fetch_page(start: str, end: str, cursor: int) -> dict:
    url = f"{_API_BASE}/{start}/{end}/{cursor}/json"
    req = urllib.request.Request(url, headers={"User-Agent": "3R-assist/1.0"})
    with urllib.request.urlopen(req, timeout=30) as resp:
        return _json.loads(resp.read())


def _parse_authors(authors_str: str) -> list[Author]:
    """Parse semicolon-separated author string from bioRxiv API."""
    authors = []
    for name in authors_str.split(";"):
        name = name.strip()
        if not name:
            continue
        parts = name.rsplit(" ", 1)
        if len(parts) == 2:
            authors.append(Author(fore_name=parts[0], last_name=parts[1]))
        else:
            authors.append(Author(last_name=name))
    return authors


def _item_to_record(item: dict) -> PubMedRecord | None:
    doi = (item.get("doi") or "").strip().lower()
    title = (item.get("title") or "").strip()
    abstract = (item.get("abstract") or "").strip()

    if not doi or not title or not abstract:
        return None

    cluster = match_cluster(title, abstract, [item.get("category", "")]) or "general"

    endpoint_text, method_text = _split_abstract(abstract)
    authors = _parse_authors(item.get("authors") or "")
    institution = (item.get("author_corresponding_institution") or "").strip()

    pub_date = item.get("date") or ""
    pub_year: int | None = None
    pub_month: int | None = None
    if pub_date:
        try:
            parts = pub_date.split("-")
            pub_year = int(parts[0])
            pub_month = int(parts[1]) if len(parts) > 1 else None
        except (ValueError, IndexError):
            pass

    published_doi = (item.get("published") or "").strip().lower()
    if published_doi in ("na", ""):
        published_doi = None

    record = PubMedRecord(
        pmid=doi,
        title=title,
        authors=authors,
        institutions=[institution] if institution else [],
        pub_year=pub_year,
        pub_month=pub_month,
        journal=item.get("server") or "bioRxiv",
        abstract_text=abstract,
        endpoint_text=endpoint_text,
        method_text=method_text,
        mesh_terms=[item.get("category", "")] if item.get("category") else [],
        cluster=cluster,
        doi=doi,
        source="biorxiv",
        published_doi=published_doi,
    )
    return record


async def run_biorxiv(
    *,
    repository: PubMedRepository,
    embedder: SentenceTransformerEmbedder,
    start_date: str = "2013-11-01",
    end_date: str | None = None,
) -> int:
    if end_date is None:
        end_date = date.today().isoformat()

    loop = asyncio.get_event_loop()

    # Fetch first page to discover total record count
    try:
        first = await loop.run_in_executor(None, _fetch_page, start_date, end_date, 0)
    except Exception as exc:
        logger.error("Failed to fetch first page: %s", exc)
        return 0

    messages = first.get("messages", [{}])
    total_available = int(messages[0].get("total", 0)) if messages else 0
    if not total_available:
        return 0

    all_cursors = list(range(0, total_available, _API_PAGE_SIZE))
    logger.info("bioRxiv ingestion: %s → %s  |  %d records, %d pages, concurrency=%d",
                start_date, end_date, total_available, len(all_cursors), _CONCURRENCY)

    total_inserted = 0
    pending_records: list[PubMedRecord] = []

    async def embed_and_insert(records: list[PubMedRecord]) -> int:
        if not records:
            return 0
        ep_texts = [r.to_endpoint_embedding_text() for r in records]
        meth_texts = [r.to_method_embedding_text() for r in records]
        ep_embs = await loop.run_in_executor(None, embedder.embed_batch, ep_texts)
        meth_embs = await loop.run_in_executor(None, embedder.embed_batch, meth_texts)
        return await repository.insert_batch(records, ep_embs, meth_embs)

    # Process in parallel chunks
    for chunk_start in range(0, len(all_cursors), _CONCURRENCY):
        chunk_cursors = all_cursors[chunk_start:chunk_start + _CONCURRENCY]

        # Fetch _CONCURRENCY pages in parallel
        tasks = [
            loop.run_in_executor(None, _fetch_page, start_date, end_date, c)
            for c in chunk_cursors
        ]
        pages = await asyncio.gather(*tasks, return_exceptions=True)

        # Parse all records from this chunk
        for page in pages:
            if isinstance(page, Exception):
                logger.warning("Page fetch failed: %s", page)
                continue
            for item in page.get("collection", []):
                record = _item_to_record(item)
                if record is not None:
                    pending_records.append(record)

            # Flush when we have enough for a full embedding batch
            while len(pending_records) >= _BATCH_SIZE:
                batch = pending_records[:_BATCH_SIZE]
                pending_records = pending_records[_BATCH_SIZE:]
                inserted = await embed_and_insert(batch)
                total_inserted += inserted
                logger.info("Inserted %d (total: %d)", inserted, total_inserted)

        done = min(chunk_cursors[-1] + _API_PAGE_SIZE, total_available)
        logger.info("Progress: %d / %d  (%.1f%%)", done, total_available, 100 * done / total_available)

        await asyncio.sleep(_CHUNK_DELAY)

    # Flush remainder
    if pending_records:
        inserted = await embed_and_insert(pending_records)
        total_inserted += inserted

    logger.info("bioRxiv ingestion complete. Total inserted: %d", total_inserted)
    return total_inserted
