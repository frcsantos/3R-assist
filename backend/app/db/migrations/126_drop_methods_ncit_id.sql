-- =============================================================================
-- Migration 126: drop methods.ncit_id.
-- The NCI Thesaurus mapping was never filled (NULL in all 47 methods) and is
-- no longer planned. No view or constraint depends on the column.
-- =============================================================================

BEGIN;

ALTER TABLE methods DROP COLUMN IF EXISTS ncit_id;

COMMIT;
