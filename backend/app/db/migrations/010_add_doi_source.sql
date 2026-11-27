-- Add DOI and source columns to support bioRxiv ingestion and cross-source deduplication.
-- doi is nullable (many PubMed records lack one); unique constraint excludes NULLs.
-- source defaults to 'pubmed' so existing rows need no backfill.

ALTER TABLE pubmed_abstracts
    ADD COLUMN IF NOT EXISTS doi    TEXT,
    ADD COLUMN IF NOT EXISTS source TEXT NOT NULL DEFAULT 'pubmed';

CREATE UNIQUE INDEX IF NOT EXISTS pubmed_doi_unique_idx
    ON pubmed_abstracts (doi)
    WHERE doi IS NOT NULL;
