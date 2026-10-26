-- =============================================================================
-- Migration 098: MAT (method 20) and its animal comparator checked against the
-- Farmacopeia Brasileira, 7th ed., vol. I (text version added to
-- docs/oecd_files): MG 5.5.2.7.1-00 (Teste de ativação de monócitos),
-- MG 5.5.2.7.2-01 (Teste de pirogênios em coelhos), MG 5.5.2.7.3-02 (LAL).
--  - MAT sources: human whole blood, PBMC or human monocytic cell lines; the
--    cells are cultured with the donor's own plasma, human AB serum or fetal
--    bovine serum.
--  - The chapter recommends the MAT instead of the rabbit pyrogen test "visando
--    à redução de uso de animais".
--  - The rabbit pyrogen test: adult rabbits of the same sex (min. 1.5 kg),
--    intravenous injection, rectal temperature.
--  - The LAL facts read by OCR in migration 096 are confirmed in the text.
-- =============================================================================

BEGIN;

UPDATE method_materials
SET name = '{"en-us": "Human whole blood, peripheral-blood mononuclear cells (PBMC) or human monocytic cell lines", "pt-br": "Sangue total humano, células mononucleares de sangue periférico (PBMC) ou linhagens celulares monocíticas humanas"}'::jsonb,
    notes = 'Farmacopeia Brasileira 7a ed., MG 5.5.2.7.1-00; blood from qualified donors; CONCEA RN 45/2019, art. 3, single paragraph (volunteer donors)'
WHERE method_id = 20 AND kind = 'sample';

INSERT INTO method_materials (method_id, kind, name, species_id, origin, animal_derived, notes)
VALUES (20, 'culture_supplement',
        '{"en-us": "Culture medium supplemented with the donor''s own plasma, human AB serum or fetal bovine serum", "pt-br": "Meio de cultura suplementado com plasma do próprio doador, soro AB humano ou soro fetal bovino"}'::jsonb,
        NULL, NULL, NULL,
        'Farmacopeia Brasileira 7a ed., MG 5.5.2.7.1-00 lists three options; only the fetal bovine serum option is animal-derived');

UPDATE methods
SET animal_procedures_avoided = '[
  {"name": {"en-us": "Rabbit pyrogen test (intravenous injection, rectal temperature)", "pt-br": "Teste de pirogênios em coelhos (injeção intravenosa, temperatura retal)"},
   "species": "rabbit", "oecd_ref": null, "r_type": "replacement", "extent": "total",
   "note": {"en-us": "Farmacopeia Brasileira MG 5.5.2.7.2-01; the MAT chapter recommends the MAT instead of this test, aiming at reducing animal use",
            "pt-br": "Farmacopeia Brasileira MG 5.5.2.7.2-01; o capítulo do MAT recomenda o MAT em detrimento deste teste, visando à redução de uso de animais"}}
]'::jsonb
WHERE id = 20;

UPDATE methods
SET animal_procedures_avoided = '[
  {"name": {"en-us": "Rabbit pyrogen test (intravenous injection, rectal temperature)", "pt-br": "Teste de pirogênios em coelhos (injeção intravenosa, temperatura retal)"},
   "species": "rabbit", "oecd_ref": null, "r_type": "replacement", "extent": "partial",
   "note": {"en-us": "Farmacopeia Brasileira MG 5.5.2.7.2-01; the BET detects endotoxins only, not non-endotoxin pyrogens",
            "pt-br": "Farmacopeia Brasileira MG 5.5.2.7.2-01; o teste de endotoxinas detecta só endotoxinas, não pirogênios não endotoxínicos"}}
]'::jsonb
WHERE id = 38;

COMMIT;
