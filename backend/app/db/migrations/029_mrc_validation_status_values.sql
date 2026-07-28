-- Migration 029: normalize method_regulatory_contexts.validation_status values
-- New allowed values:
--   - validated
--   - in_process_of_validation
--   - not_validated

DO $$
DECLARE
  rec record;
BEGIN
  -- Remove any previous CHECK constraints that validate this column,
  -- regardless of historical constraint names.
  FOR rec IN
    SELECT c.conname
    FROM pg_constraint c
    JOIN pg_class t ON t.oid = c.conrelid
    JOIN pg_namespace n ON n.oid = t.relnamespace
    WHERE c.contype = 'c'
      AND n.nspname = 'public'
      AND t.relname = 'method_regulatory_contexts'
      AND pg_get_constraintdef(c.oid) ILIKE '%validation_status%'
  LOOP
    EXECUTE format(
      'ALTER TABLE method_regulatory_contexts DROP CONSTRAINT IF EXISTS %I',
      rec.conname
    );
  END LOOP;
END $$;

UPDATE method_regulatory_contexts
SET validation_status = CASE
  WHEN validation_status = 'validated' THEN 'validated'
  WHEN validation_status = 'accepted' THEN 'in_process_of_validation'
  WHEN validation_status = 'emerging' THEN 'not_validated'
  WHEN validation_status = 'in_process_of_validation' THEN 'in_process_of_validation'
  WHEN validation_status = 'not_validated' THEN 'not_validated'
  ELSE 'not_validated'
END;

ALTER TABLE method_regulatory_contexts
  ADD CONSTRAINT method_regulatory_contexts_validation_status_check CHECK (
    validation_status IN (
      'validated',
      'in_process_of_validation',
      'not_validated'
    )
  );
