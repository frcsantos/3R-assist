-- Replace regulatory_ref with regulation_date on method_validation_contexts.

ALTER TABLE method_validation_contexts
  DROP COLUMN IF EXISTS regulatory_ref;

ALTER TABLE method_validation_contexts
  ADD COLUMN IF NOT EXISTS regulation_date DATE;

COMMENT ON COLUMN method_validation_contexts.regulation_date IS
  'Date of the regulation / recognition / adoption for this context (YYYY-MM-DD).';
