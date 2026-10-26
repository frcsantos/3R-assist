-- =============================================================================
-- Migration 080: applications review.
--  1. pt-br label of `education-training` standardised to "Educação e treinamento"
--     (to be confirmed by curators, docs/decisoes_curadoria.md).
--  2. Add the application categories that were missing:
--     - routine-production (4): MAT (20), LAL (38), rFC (56) - pharmacopoeia
--       quality-control tests for injectables (batch release);
--     - environmental-protection (6): TG 212 (51), TG 236 (53), TG 319A (54),
--       TG 319B (55) - fish ecotoxicity / bioaccumulation.
--     `regulatory-use` (3) is kept.
-- =============================================================================

BEGIN;

UPDATE applications
SET name = jsonb_set(name, '{pt-br}', to_jsonb('Educação e treinamento'::text)),
    updated_at = NOW()
WHERE slug = 'education-training';

UPDATE methods
SET application_ids = application_ids || 4
WHERE id IN (20, 38, 56) AND NOT (4 = ANY(application_ids));

UPDATE methods
SET application_ids = application_ids || 6
WHERE id IN (51, 53, 54, 55) AND NOT (6 = ANY(application_ids));

COMMIT;
