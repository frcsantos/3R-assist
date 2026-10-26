-- =============================================================================
-- Migration 113: documents #15 (OECD TG 428) date and slug 2024-11-23 ->
-- 2004-11-23 (citation already reads OECD (2004)).
-- =============================================================================

BEGIN;

UPDATE documents
SET "date" = DATE '2004-11-23',
    slug = 'oecd-test-no-428-2004-11-23-skin-absorption-in-vitro-method'
WHERE id = 15
  AND slug = 'oecd-test-no-428-2024-11-23-skin-absorption-in-vitro-method';

COMMIT;
