-- =============================================================================
-- Migration 118: animal_use `embryos_and_larvae` + provisional curation values.
--  1. New animal_use value `embryos_and_larvae` (CHECK + enum_terms label).
--  2. TG 212 (51) and TG 236 (53), fish embryo / sac-fry tests: live_animals ->
--     embryos_and_larvae. Pending confirmation (decisoes_curadoria.md item 18).
--  3. TG 471, 473, 476 and 487 (17, 45, 18, 19; animal_use was NULL): assume the
--     rat-liver S9 is prepared in the laboratory -> animals_killed_for_tissue,
--     like TG 490 (46). Pending confirmation (decisoes_curadoria.md item 1).
-- =============================================================================

BEGIN;

ALTER TABLE methods DROP CONSTRAINT IF EXISTS methods_animal_use_check;
ALTER TABLE methods
  ADD CONSTRAINT methods_animal_use_check CHECK (
    animal_use IS NULL
    OR animal_use IN (
      'none',
      'animal_derived_material',
      'slaughterhouse_byproduct',
      'animals_killed_for_tissue',
      'live_animals',
      'mixed_or_variable',
      'embryos_and_larvae'
    )
  );

COMMENT ON COLUMN methods.animal_use IS
  'How the method uses animals or animal materials: none | animal_derived_material | slaughterhouse_byproduct | animals_killed_for_tissue | live_animals | mixed_or_variable | embryos_and_larvae.';

INSERT INTO enum_terms (domain, code, name, sort_order)
VALUES (
  'animal_use',
  'embryos_and_larvae',
  '{"en-us": "Embryos and larvae", "pt-br": "Embriões e larvas"}'::jsonb,
  7
)
ON CONFLICT (domain, code) DO NOTHING;

UPDATE methods
SET animal_use = 'embryos_and_larvae'
WHERE id IN (51, 53)
  AND animal_use = 'live_animals';

UPDATE methods
SET animal_use = 'animals_killed_for_tissue'
WHERE id IN (17, 18, 19, 45)
  AND animal_use IS NULL;

COMMIT;
