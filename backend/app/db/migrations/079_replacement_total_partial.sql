-- =============================================================================
-- Migration 079: state in every replacement_rationale whether the replacement
-- is total or partial (review plan, section 3). Classification proposed by
-- the data team; to be confirmed by curators (docs/decisoes_curadoria.md).
-- =============================================================================

BEGIN;

UPDATE methods m
SET replacement_rationale = jsonb_build_object(
  'en-us', v.en || (m.replacement_rationale->>'en-us'),
  'pt-br', v.pt || (m.replacement_rationale->>'pt-br'))
FROM (VALUES
  (3,  'Total replacement. ', 'Substituição total. '),
  (5,  'Total replacement. ', 'Substituição total. '),
  (16, 'Total replacement. ', 'Substituição total. '),
  (20, 'Total replacement. ', 'Substituição total. '),
  (39, 'Total replacement. ', 'Substituição total. '),
  (56, 'Total replacement. ', 'Substituição total. '),
  (1,  'Total or partial replacement. ', 'Substituição total ou parcial. '),
  (22, 'Partial replacement; total if accepted by the regulatory authority. ', 'Substituição parcial; total se aceita pela autoridade regulatória. '),
  (4,  'Partial replacement. ', 'Substituição parcial. '),
  (6,  'Partial replacement. ', 'Substituição parcial. '),
  (7,  'Partial replacement. ', 'Substituição parcial. '),
  (8,  'Partial replacement. ', 'Substituição parcial. '),
  (9,  'Partial replacement. ', 'Substituição parcial. '),
  (10, 'Partial replacement. ', 'Substituição parcial. '),
  (11, 'Partial replacement. ', 'Substituição parcial. '),
  (12, 'Partial replacement. ', 'Substituição parcial. '),
  (30, 'Partial replacement. ', 'Substituição parcial. '),
  (33, 'Partial replacement. ', 'Substituição parcial. '),
  (34, 'Partial replacement. ', 'Substituição parcial. '),
  (35, 'Partial replacement. ', 'Substituição parcial. '),
  (38, 'Partial replacement. ', 'Substituição parcial. '),
  (40, 'Partial replacement. ', 'Substituição parcial. '),
  (41, 'Partial replacement. ', 'Substituição parcial. '),
  (42, 'Partial replacement. ', 'Substituição parcial. '),
  (43, 'Partial replacement. ', 'Substituição parcial. '),
  (47, 'Partial replacement. ', 'Substituição parcial. '),
  (49, 'Partial replacement. ', 'Substituição parcial. '),
  (50, 'Partial replacement. ', 'Substituição parcial. '),
  (53, 'Partial replacement. ', 'Substituição parcial. ')
) AS v(id, en, pt)
WHERE m.id = v.id
  AND m.replacement_rationale IS NOT NULL
  AND m.replacement_rationale->>'en-us' NOT LIKE 'Total%'
  AND m.replacement_rationale->>'en-us' NOT LIKE 'Partial%';

COMMIT;
