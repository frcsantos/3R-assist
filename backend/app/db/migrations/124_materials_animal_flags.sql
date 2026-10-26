-- =============================================================================
-- Migration 124: animal flags on method_materials that need no curation.
--  - Rows 70 (serum), 72 and 73 (anti-rabies antibodies) have origin = 'animal'
--    but animal_derived NULL -> true.
--  - Rows 77, 78 and 82 (5% fetal bovine serum) have animal_derived = true but
--    origin NULL -> 'animal'.
-- Animal cell lines (rows 8, 9, 10, 12, 40, 57) and the 3T3-J2 feeder cells
-- (rows 80, 81, 84) stay as they are: the animal_derived rule for cell lines
-- is open in docs/decisoes_curadoria.md.
-- =============================================================================

BEGIN;

UPDATE method_materials
SET animal_derived = TRUE
WHERE id IN (70, 72, 73)
  AND origin = 'animal'
  AND animal_derived IS NULL;

UPDATE method_materials
SET origin = 'animal'
WHERE id IN (77, 78, 82)
  AND origin IS NULL
  AND animal_derived;

COMMIT;
