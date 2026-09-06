-- =============================================================================
-- Migration 033: documents.description (localized JSONB)
-- Shape: {"en-us": "...", "pt-br": "..."}
-- =============================================================================

BEGIN;

ALTER TABLE documents
  ADD COLUMN IF NOT EXISTS description JSONB;

UPDATE documents
SET description = '{"en-us":"","pt-br":""}'::jsonb
WHERE description IS NULL;

ALTER TABLE documents
  ALTER COLUMN description SET NOT NULL,
  ALTER COLUMN description SET DEFAULT '{"en-us":"","pt-br":""}'::jsonb;

COMMENT ON COLUMN documents.description IS
  'Localized document description: {"en-us": "...", "pt-br": "..."}';

COMMIT;
