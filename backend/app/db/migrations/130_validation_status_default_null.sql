-- =============================================================================
-- Migration 130: methods.validation_status defaults to NULL (not assessed)
-- instead of 'unclear'. Existing rows are not changed.
-- =============================================================================

BEGIN;

ALTER TABLE methods ALTER COLUMN validation_status DROP DEFAULT;

COMMIT;
