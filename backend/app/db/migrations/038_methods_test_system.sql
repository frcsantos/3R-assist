-- =============================================================================
-- Migration 038: methods.test_system (JSONB multi-select)
-- Values: in_silico | in_chemico | in_vitro | ex_vivo | in_vivo | hybrid | unclear
-- =============================================================================

ALTER TABLE methods
  ADD COLUMN IF NOT EXISTS test_system JSONB;

ALTER TABLE methods
  DROP CONSTRAINT IF EXISTS methods_test_system_is_array;
ALTER TABLE methods
  DROP CONSTRAINT IF EXISTS methods_test_system_values_check;

ALTER TABLE methods
  ADD CONSTRAINT methods_test_system_is_array CHECK (
    test_system IS NULL
    OR jsonb_typeof(test_system) = 'array'
  );

ALTER TABLE methods
  ADD CONSTRAINT methods_test_system_values_check CHECK (
    test_system IS NULL
    OR test_system <@ '[
      "in_silico",
      "in_chemico",
      "in_vitro",
      "ex_vivo",
      "in_vivo",
      "hybrid",
      "unclear"
    ]'::jsonb
  );

COMMENT ON COLUMN methods.test_system IS
  'Test system kinds (multi-select JSON array): '
  'in_silico | in_chemico | in_vitro | ex_vivo | in_vivo | hybrid | unclear.';

CREATE INDEX IF NOT EXISTS idx_methods_test_system
  ON methods USING gin (test_system);
