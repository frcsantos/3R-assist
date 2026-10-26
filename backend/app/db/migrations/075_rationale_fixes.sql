-- =============================================================================
-- Migration 075: replacement_rationale fixes.
--  - TG 495 (method 50): pt-br spelling.
--  - DFA (30) and RT-PCR (35): the text described cell-culture virus isolation
--    (RTCIT). Replaced by a statement based on CONCEA Resolution 75/2026
--    (alternatives to mouse inoculation; art. 4 allows it only as last resort).
-- =============================================================================

BEGIN;

UPDATE methods
SET replacement_rationale = jsonb_set(replacement_rationale, '{pt-br}',
  to_jsonb('O ensaio de ROS é um método in chemico que avalia a fototoxicidade sem o uso de animais.'::text))
WHERE oecd_ref = 'TG 495';

UPDATE methods SET replacement_rationale = jsonb_build_object(
  'en-us', 'Recognized by CONCEA Resolution 75/2026 as an alternative to mouse inoculation for rabies diagnosis; mouse inoculation is allowed only as a last resort when recognized alternatives leave the diagnosis inconclusive.',
  'pt-br', 'Reconhecido pela Resolução CONCEA nº 75/2026 como alternativa à inoculação em camundongos para o diagnóstico da raiva; a inoculação em camundongos só pode ser usada como último recurso, quando as alternativas reconhecidas deixam o diagnóstico inconclusivo.')
WHERE id IN (30, 35);

COMMIT;
