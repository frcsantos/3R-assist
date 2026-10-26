-- =============================================================================
-- Migration 077: test_system review.
--  1. Allow the new value `in_data` in methods.test_system.
--  2. Data fixes:
--     - DFA (30) and dRIT (33): ex_vivo -> in_vitro (same as RTCIT and RT-PCR).
--     - TG 428 (21): in_vitro -> ex_vivo (excised skin).
--     - Acellular assays -> in_chemico: TG 435 (5), TG 496 (49), TG 493 (42),
--       LAL (38), rFC (56).
--     - TG 442A (14) and TG 442B (15): add ex_vivo (in vivo exposure, ex vivo
--       lymph node readout).
-- =============================================================================

BEGIN;

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
      "hybrid",
      "unclear"
    ]'::jsonb
  );

COMMENT ON COLUMN methods.test_system IS
  'Test system kinds (multi-select JSON array): '
  'in_silico | in_chemico | in_data | in_vitro | ex_vivo | in_vivo | hybrid | unclear.';

UPDATE methods SET test_system = '["in_vitro"]'::jsonb  WHERE id IN (30, 33);
UPDATE methods SET test_system = '["ex_vivo"]'::jsonb   WHERE id = 21;
UPDATE methods SET test_system = '["in_chemico"]'::jsonb WHERE id IN (5, 38, 42, 49, 56);
UPDATE methods SET test_system = '["in_vivo", "ex_vivo"]'::jsonb WHERE id IN (14, 15);

COMMIT;
