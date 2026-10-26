-- =============================================================================
-- Migration 094: conventional-test notes checked against the full texts of
-- TG 404, 405, 406, 401, 203, 440, 441 and 305.
--  - TG 401 was deleted by the OECD on 17 December 2002 (the file in
--    docs/oecd_files is only the deletion notice): note added to the elements
--    that refer to it.
--  - GD 129 gives the LD50 reference values for "rats and mice": the species of
--    its element is left open instead of "rat".
--  - Species confirmed in the texts: TG 404 and 405 albino rabbit, TG 406
--    guinea pig, TG 440 rat (mouse also accepted), TG 441 rat.
-- =============================================================================

BEGIN;

UPDATE methods m
SET animal_procedures_avoided = (
  SELECT jsonb_agg(
    CASE WHEN e->>'oecd_ref' = 'TG 401'
      THEN e || jsonb_build_object(
             'note', jsonb_build_object(
               'en-us', 'TG 401 was deleted by the OECD on 17 December 2002',
               'pt-br', 'A TG 401 foi retirada pela OCDE em 17 de dezembro de 2002'))
           || CASE WHEN m.id = 22 THEN '{"species": null}'::jsonb ELSE '{}'::jsonb END
      ELSE e END
    ORDER BY ord)
  FROM jsonb_array_elements(m.animal_procedures_avoided) WITH ORDINALITY AS t(e, ord)
)
WHERE m.id IN (22, 23, 24, 25);

COMMIT;
