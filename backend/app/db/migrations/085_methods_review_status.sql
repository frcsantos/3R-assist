-- =============================================================================
-- Migration 085: methods.review_status (review plan: "somente após essa revisão
-- o método deve ser considerado validado").
-- Separate from `active` (published in the platform) and from
-- `validation_status` (scientific / regulatory standing).
-- All existing methods start as not_reviewed.
-- =============================================================================

BEGIN;

ALTER TABLE methods
  ADD COLUMN review_status TEXT NOT NULL DEFAULT 'not_reviewed'
  CHECK (review_status IN ('not_reviewed', 'in_review', 'reviewed'));

COMMENT ON COLUMN methods.review_status IS
  'Curation review state: not_reviewed | in_review | reviewed. Independent of active and validation_status.';

COMMIT;
