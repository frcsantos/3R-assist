-- =============================================================================
-- Migration 037: methods.animal_use (controlled vocabulary)
-- Values: none | animal_derived_material | slaughterhouse_byproduct |
--         animals_killed_for_tissue | live_animals | mixed_or_variable
-- =============================================================================

ALTER TABLE methods
  ADD COLUMN IF NOT EXISTS animal_use TEXT;

ALTER TABLE methods
  DROP CONSTRAINT IF EXISTS methods_animal_use_check;

ALTER TABLE methods
  ADD CONSTRAINT methods_animal_use_check CHECK (
    animal_use IS NULL
    OR animal_use IN (
      'none',
      'animal_derived_material',
      'slaughterhouse_byproduct',
      'animals_killed_for_tissue',
      'live_animals',
      'mixed_or_variable'
    )
  );

COMMENT ON COLUMN methods.animal_use IS
  'How the method uses animals or animal materials: '
  'none | animal_derived_material | slaughterhouse_byproduct | '
  'animals_killed_for_tissue | live_animals | mixed_or_variable.';
