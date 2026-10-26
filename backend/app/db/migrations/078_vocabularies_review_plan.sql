-- =============================================================================
-- Migration 078: vocabularies from the review plan (Revisao.md) + endpoints.
--  1. methods.test_system: remove `hybrid`.
--  2. methods.validation_status: add `recognized`, remove `not_evaluated`
--     (default becomes `unclear`; no row used `not_evaluated`).
--  3. regulations.regulatory_status: add `recognized`.
--  4. endpoints: add the more specific endpoints, keeping the general ones:
--     MAT (20) + 5.1.1 Pyrogenicity (49); TG 487 (19) + 2.4.1.1 Mutagenicity (23).
-- =============================================================================

BEGIN;

-- 1 -------------------------------------------------------------------------
ALTER TABLE methods DROP CONSTRAINT IF EXISTS methods_test_system_values_check;
ALTER TABLE methods
  ADD CONSTRAINT methods_test_system_values_check CHECK (
    test_system IS NULL
    OR test_system <@ '[
      "in_silico",
      "in_chemico",
      "in_data",
      "in_vitro",
      "ex_vivo",
      "in_vivo",
      "unclear"
    ]'::jsonb
  );

COMMENT ON COLUMN methods.test_system IS
  'Test system kinds (multi-select JSON array): '
  'in_silico | in_chemico | in_data | in_vitro | ex_vivo | in_vivo | unclear.';

-- 2 -------------------------------------------------------------------------
UPDATE methods SET validation_status = 'unclear' WHERE validation_status = 'not_evaluated';

ALTER TABLE methods DROP CONSTRAINT IF EXISTS methods_validation_status_check;
ALTER TABLE methods
  ADD CONSTRAINT methods_validation_status_check CHECK (
    validation_status IN (
      'recognized',
      'under_validation',
      'validated',
      'partially_validated',
      'not_validated',
      'unclear'
    )
  );
ALTER TABLE methods ALTER COLUMN validation_status SET DEFAULT 'unclear';

COMMENT ON COLUMN methods.validation_status IS
  'Scientific validation standing of the method: recognized | under_validation | validated | partially_validated | not_validated | unclear.';

-- 3 -------------------------------------------------------------------------
ALTER TABLE regulations DROP CONSTRAINT IF EXISTS regulations_regulatory_status_check;
ALTER TABLE regulations
  ADD CONSTRAINT regulations_regulatory_status_check CHECK (
    regulatory_status IS NULL
    OR regulatory_status IN ('not_approved', 'approved', 'recognized', 'recommended', 'mandatory')
  );

-- 4 -------------------------------------------------------------------------
UPDATE methods SET endpoints = ARRAY[48, 49, 51] WHERE id = 20 AND endpoints = ARRAY[48, 51];
UPDATE methods SET endpoints = ARRAY[22, 23]     WHERE id = 19 AND endpoints = ARRAY[22];

COMMIT;
