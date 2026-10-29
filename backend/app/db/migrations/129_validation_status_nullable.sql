-- =============================================================================
-- Migration 129: methods.validation_status accepts NULL (status not assessed
-- or not yet decided by curation). The column default stays 'unclear'.
-- =============================================================================

BEGIN;

ALTER TABLE methods ALTER COLUMN validation_status DROP NOT NULL;

ALTER TABLE methods DROP CONSTRAINT IF EXISTS methods_validation_status_check;
ALTER TABLE methods
  ADD CONSTRAINT methods_validation_status_check CHECK (
    validation_status IS NULL
    OR validation_status IN (
      'recognized', 'under_validation', 'validated', 'partially_validated',
      'not_validated', 'unclear'
    )
  );

COMMIT;
