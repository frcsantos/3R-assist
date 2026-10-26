-- =============================================================================
-- Migration 070: pt-br name fixes.
--  - TG 495: fix spelling (Espécies, Oxigênio).
--  - TG 319A / 319B: use "clearance" in both (as in the CONCEA RN 56/2022
--    quote), capitalisation aligned with 069.
-- =============================================================================

BEGIN;

UPDATE methods m
SET name = jsonb_set(m.name, '{pt-br}', to_jsonb(v.pt))
FROM (VALUES
  (50, 'Ensaio de Espécies Reativas de Oxigênio (ROS) para Fotorreatividade'),
  (54, 'Determinação do Clearance Intrínseco In Vitro Usando Hepatócitos Criopreservados de Truta Arco-Íris (RT-HEP)'),
  (55, 'Determinação do Clearance Intrínseco In Vitro Utilizando Fração Subcelular S9 de Fígado de Truta Arco-Íris (RT-S9)')
) AS v(id, pt)
WHERE m.id = v.id;

COMMIT;
