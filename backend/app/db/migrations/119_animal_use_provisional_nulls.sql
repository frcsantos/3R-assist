-- =============================================================================
-- Migration 119: provisional animal_use for methods that were NULL, where the
-- registered materials point to one value. Pending confirmation in
-- docs/decisoes_curadoria.md (items 2, 5 and 6). Only rows still NULL change.
--   animal_derived_material  8, 12, 16, 22, 41, 43, 44, 47  (animal serum, item 5)
--   mixed_or_variable        1, 3, 11  (RhE models vary by laboratory, items 2/5)
--   none                     42, 56    (recombinant reagents, item 6)
-- Left NULL: 5 (TG 435), 49 (TG 496) and 39 (TG 492B): origin not declared.
-- =============================================================================

BEGIN;

UPDATE methods SET animal_use = 'animal_derived_material'
WHERE id IN (8, 12, 16, 22, 41, 43, 44, 47) AND animal_use IS NULL;

UPDATE methods SET animal_use = 'mixed_or_variable'
WHERE id IN (1, 3, 11) AND animal_use IS NULL;

UPDATE methods SET animal_use = 'none'
WHERE id IN (42, 56) AND animal_use IS NULL;

COMMIT;
