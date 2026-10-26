-- =============================================================================
-- Migration 074: animal_use corrections (ADR-026).
--  - TG 430 (TER): skin discs come from rats killed for the assay
--    -> animals_killed_for_tissue (was slaughterhouse_byproduct).
--  - TG 319B (RT-S9): liver from trout killed for the S9 fraction, as TG 319A
--    -> animals_killed_for_tissue (was slaughterhouse_byproduct).
--  - TG 442C (DPRA) and TG 495 (ROS): in chemico, no animal or derived
--    material (ADR-026 rule 3) -> none (was NULL).
-- Remaining open items are listed in docs/animal_use_curation.md.
-- =============================================================================

BEGIN;

UPDATE methods SET animal_use = 'animals_killed_for_tissue'
WHERE oecd_ref IN ('TG 430', 'TG 319B') AND animal_use = 'slaughterhouse_byproduct';

UPDATE methods SET animal_use = 'none'
WHERE oecd_ref IN ('TG 442C', 'TG 495') AND animal_use IS NULL;

COMMIT;
