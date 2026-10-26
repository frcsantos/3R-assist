-- =============================================================================
-- Migration 103: official Ph. Eur. chapter titles supplied by the curators:
--   2.6.8  Pyrogens
--   2.6.14 Bacterial endotoxins
--   2.6.30 Monocyte-activation test
--   2.6.32 Test for bacterial endotoxins using recombinant factor C (already used)
-- English names of the MAT (20) and the LAL/BET (38) follow these titles; the
-- Portuguese names (RN texts) are unchanged. The rabbit pyrogen test elements
-- of MAT and LAL cite Ph. Eur. 2.6.8. Only the titles were supplied, not the
-- chapter texts.
-- =============================================================================

BEGIN;

UPDATE methods m
SET name = jsonb_set(m.name, '{en-us}', to_jsonb(v.en::text))
FROM (VALUES
  (20, 'Monocyte-activation test'),
  (38, 'Bacterial endotoxins')
) AS v(id, en)
WHERE m.id = v.id;

UPDATE methods m
SET animal_procedures_avoided = (
  SELECT jsonb_agg(e || '{"oecd_ref": "Ph. Eur. 2.6.8"}'::jsonb ORDER BY ord)
  FROM jsonb_array_elements(m.animal_procedures_avoided) WITH ORDINALITY AS t(e, ord)
)
WHERE m.id IN (20, 38);

COMMIT;
