-- =============================================================================
-- Migration 030: documents.doc_ref → doc_citation (localized JSONB)
-- Shape: {"en-us": "...", "pt-br": "..."}
-- =============================================================================

BEGIN;

ALTER TABLE documents
  ADD COLUMN IF NOT EXISTS doc_citation JSONB;

UPDATE documents
SET doc_citation = jsonb_build_object(
  'en-us', doc_ref,
  'pt-br', doc_ref
)
WHERE doc_citation IS NULL;

ALTER TABLE documents
  ALTER COLUMN doc_citation SET NOT NULL;

ALTER TABLE documents
  DROP COLUMN IF EXISTS doc_ref;

COMMENT ON COLUMN documents.doc_citation IS
  'Localized document citation / reference key: {"en-us": "...", "pt-br": "..."} (e.g. OECD TG 439, RN 18/2014).';

COMMIT;
