-- =============================================================================
-- Migration 090: animal_procedures_avoided for the methods that replace a
-- well-defined conventional animal test, and OECD references for the ones
-- already filled.
-- The conventional test guidelines come from the OHT table (TG 404 skin
-- irritation/corrosion, TG 405 eye, TG 406 and TG 429 skin sensitisation,
-- TG 401 acute oral toxicity, TG 203 fish). Species of each conventional
-- test is from the guideline; confirm with curators.
-- `extent` follows replacement_rationale (migration 079). TG 439 is
-- stand-alone or partial; recorded here as total (stand-alone).
-- Not filled (curators): LLNA variants (TG 429, 442A, 442B), TG 425, TG 421,
-- TG 319B, phototoxicity and endocrine methods.
-- =============================================================================

BEGIN;

-- Skin: TG 404 (rabbit) --------------------------------------------------------
UPDATE methods m
SET animal_procedures_avoided = jsonb_build_array(jsonb_build_object(
  'name', jsonb_build_object('en-us', 'In vivo acute dermal irritation/corrosion test',
                             'pt-br', 'Teste in vivo de irritação/corrosão cutânea aguda'),
  'species', 'rabbit', 'oecd_ref', 'TG 404',
  'r_type', 'replacement', 'extent', v.extent))
FROM (VALUES (1, 'total'), (3, 'total'), (4, 'partial'), (5, 'total')) AS v(id, extent)
WHERE m.id = v.id;

-- Eye: TG 405 (rabbit) -----------------------------------------------------------
UPDATE methods m
SET animal_procedures_avoided = jsonb_build_array(jsonb_build_object(
  'name', jsonb_build_object('en-us', 'In vivo acute eye irritation/corrosion test',
                             'pt-br', 'Teste in vivo de irritação/corrosão ocular aguda'),
  'species', 'rabbit', 'oecd_ref', 'TG 405',
  'r_type', 'replacement', 'extent', v.extent))
FROM (VALUES (6, 'partial'), (7, 'partial'), (8, 'partial'), (9, 'partial'),
             (39, 'total'), (40, 'partial'), (47, 'partial'), (49, 'partial')) AS v(id, extent)
WHERE m.id = v.id;

-- Skin sensitisation: TG 406 (guinea pig) and TG 429 (mouse) ------------------------------
UPDATE methods
SET animal_procedures_avoided = '[
  {"name": {"en-us": "Skin sensitisation test in guinea pigs", "pt-br": "Teste de sensibilização cutânea em cobaias"},
   "species": "guinea_pig", "oecd_ref": "TG 406", "r_type": "replacement", "extent": "partial"},
  {"name": {"en-us": "Local lymph node assay (LLNA) in mice", "pt-br": "Ensaio do linfonodo local (LLNA) em camundongos"},
   "species": "mouse", "oecd_ref": "TG 429", "r_type": "replacement", "extent": "partial"}
]'::jsonb
WHERE id IN (10, 11, 12);

-- Acute oral toxicity: TG 401 (rat), now with reference ------------------------------------
UPDATE methods SET animal_procedures_avoided = '[
  {"name": {"en-us": "In vivo acute oral toxicity tests (LD50 determination)", "pt-br": "Testes de toxicidade oral aguda in vivo (determinação da DL50)"},
   "species": "rat", "oecd_ref": "TG 401", "r_type": "reduction", "extent": null},
  {"name": {"en-us": "In vivo acute oral toxicity tests (LD50 determination)", "pt-br": "Testes de toxicidade oral aguda in vivo (determinação da DL50)"},
   "species": "rat", "oecd_ref": "TG 401", "r_type": "replacement", "extent": "partial"}
]'::jsonb WHERE id = 22;

UPDATE methods SET animal_procedures_avoided = '[
  {"name": {"en-us": "Traditional LD50 acute oral toxicity test", "pt-br": "Teste tradicional de toxicidade oral aguda (DL50)"},
   "species": "rat", "oecd_ref": "TG 401", "r_type": "reduction", "extent": null},
  {"name": {"en-us": "Traditional LD50 acute oral toxicity test", "pt-br": "Teste tradicional de toxicidade oral aguda (DL50)"},
   "species": "rat", "oecd_ref": "TG 401", "r_type": "refinement", "extent": null}
]'::jsonb WHERE id = 23;

UPDATE methods SET animal_procedures_avoided = '[
  {"name": {"en-us": "Conventional acute oral toxicity tests", "pt-br": "Testes convencionais de toxicidade aguda oral"},
   "species": "rat", "oecd_ref": "TG 401", "r_type": "reduction", "extent": null}
]'::jsonb WHERE id = 24;

-- Fish: TG 203 --------------------------------------------------------------------------------
UPDATE methods SET animal_procedures_avoided = '[
  {"name": {"en-us": "Acute toxicity tests on juvenile or adult fish", "pt-br": "Testes de toxicidade aguda em peixes juvenis ou adultos"},
   "species": null, "oecd_ref": "TG 203", "r_type": "replacement", "extent": "partial"}
]'::jsonb WHERE id = 53;

COMMIT;
