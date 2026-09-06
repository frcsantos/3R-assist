-- =============================================================================
-- Migration 045: regulations.regulatory_body / regulatory_citation → JSONB
-- Shape: {"en-us": "...", "pt-br": "..."}
-- regulatory_doc_id stays INTEGER FK → documents(id).
-- =============================================================================

BEGIN;

ALTER TABLE regulations
  ALTER COLUMN regulatory_body TYPE JSONB
  USING (
    CASE
      WHEN regulatory_body IS NULL OR BTRIM(regulatory_body) = '' THEN NULL
      ELSE jsonb_build_object(
        'en-us', regulatory_body,
        'pt-br', regulatory_body
      )
    END
  );

ALTER TABLE regulations
  ALTER COLUMN regulatory_citation TYPE JSONB
  USING (
    CASE
      WHEN regulatory_citation IS NULL OR BTRIM(regulatory_citation) = '' THEN NULL
      ELSE jsonb_build_object(
        'en-us', regulatory_citation,
        'pt-br', regulatory_citation
      )
    END
  );

COMMENT ON COLUMN regulations.regulatory_body IS
  'Localized issuing body: {"en-us":"...","pt-br":"..."} '
  '(e.g. OECD/OCDE, CONCEA).';
COMMENT ON COLUMN regulations.regulatory_citation IS
  'Localized bibliographic citation: {"en-us":"...","pt-br":"..."}. '
  'API falls back to documents.doc_citation when empty.';

COMMIT;
