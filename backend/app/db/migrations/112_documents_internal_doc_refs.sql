-- =============================================================================
-- Migration 112: documents.internal_doc_refs INTEGER[]
-- Ids of other documents cited by this document that also exist in the
-- documents catalogue. Postgres cannot enforce FKs on array elements, so
-- integrity is by convention (same as methods.application_ids); a document
-- may not reference itself.
-- =============================================================================

BEGIN;

ALTER TABLE documents
  ADD COLUMN IF NOT EXISTS internal_doc_refs INTEGER[] NOT NULL DEFAULT '{}';

ALTER TABLE documents
  DROP CONSTRAINT IF EXISTS documents_internal_doc_refs_no_self;
ALTER TABLE documents
  ADD CONSTRAINT documents_internal_doc_refs_no_self
  CHECK (NOT (id = ANY (internal_doc_refs)));

CREATE INDEX IF NOT EXISTS idx_documents_internal_doc_refs
  ON documents USING GIN (internal_doc_refs);

COMMENT ON COLUMN documents.internal_doc_refs IS
  'Ids of documents cited by this document that also exist in documents.';

COMMIT;
