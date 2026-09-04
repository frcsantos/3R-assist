-- =============================================================================
-- Migration 047: regulations field rename + backfill from documents
--
-- Backfill:
--   regulation_status     → 'approved' for all rows
--   regulatory_citation   → NULL for all rows
--   regulatory_body       → documents.institution via regulatory_doc_id
--   regulation_date       → documents.date via regulatory_doc_id
--
-- Rename:
--   regulation_status  → regulatory_status
--   regulation_date    → regulatory_date
--   regulation_purpose → regulatory_purpose
-- =============================================================================

BEGIN;

UPDATE regulations
SET
  regulation_status = 'approved',
  regulatory_citation = NULL;

UPDATE regulations r
SET
  regulatory_body = d.institution,
  regulation_date = d.date
FROM documents d
WHERE r.regulatory_doc_id = d.id;

ALTER TABLE regulations
  RENAME COLUMN regulation_status TO regulatory_status;

ALTER TABLE regulations
  RENAME COLUMN regulation_date TO regulatory_date;

ALTER TABLE regulations
  RENAME COLUMN regulation_purpose TO regulatory_purpose;

DO $$
BEGIN
  IF EXISTS (
    SELECT 1 FROM pg_constraint
    WHERE conname = 'regulations_regulation_status_check'
  ) THEN
    ALTER TABLE regulations
      RENAME CONSTRAINT regulations_regulation_status_check
      TO regulations_regulatory_status_check;
  END IF;
END $$;

COMMENT ON COLUMN regulations.regulatory_status IS
  'Regulatory standing: not_approved | approved | recommended | mandatory.';
COMMENT ON COLUMN regulations.regulatory_date IS
  'Date of the regulation / recognition / adoption (YYYY-MM-DD). '
  'Backfilled from documents.date when regulatory_doc_id is set.';
COMMENT ON COLUMN regulations.regulatory_purpose IS
  'Localized recognition purpose: {"en-us":"...","pt-br":"..."}.';
COMMENT ON COLUMN regulations.regulatory_body IS
  'Localized issuing body: {"en-us":"...","pt-br":"..."} '
  '(copied from documents.institution when regulatory_doc_id is set).';
COMMENT ON COLUMN regulations.regulatory_citation IS
  'Localized bibliographic citation: {"en-us":"...","pt-br":"..."}. '
  'API falls back to documents.doc_citation when empty.';

COMMIT;
