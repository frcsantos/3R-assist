-- =============================================================================
-- Migration 084: methods.animal_procedures_avoided (review plan, section 7).
-- JSONB array; each element describes an animal procedure the method
-- replaces, reduces or refines:
--   {
--     "name":     {"en-us": "...", "pt-br": "..."},
--     "species":  "rabbit" | null,          -- species.slug of the conventional procedure
--     "oecd_ref": "TG 404" | null,
--     "r_type":   "replacement" | "reduction" | "refinement",
--     "extent":   "total" | "partial"       -- required when r_type = "replacement"
--   }
-- Seeded only with procedures named in the existing rationales; the rest is
-- for curators.
-- =============================================================================

BEGIN;

ALTER TABLE methods ADD COLUMN animal_procedures_avoided JSONB;

ALTER TABLE methods
  ADD CONSTRAINT methods_animal_procedures_avoided_is_array CHECK (
    animal_procedures_avoided IS NULL
    OR jsonb_typeof(animal_procedures_avoided) = 'array'
  ),
  ADD CONSTRAINT methods_animal_procedures_avoided_r_type CHECK (
    animal_procedures_avoided IS NULL
    OR NOT jsonb_path_exists(
      animal_procedures_avoided,
      '$[*] ? (!(@.r_type == "replacement" || @.r_type == "reduction" || @.r_type == "refinement"))'
    )
  ),
  ADD CONSTRAINT methods_animal_procedures_avoided_extent CHECK (
    animal_procedures_avoided IS NULL
    OR NOT jsonb_path_exists(
      animal_procedures_avoided,
      '$[*] ? (@.r_type == "replacement" && !(@.extent == "total" || @.extent == "partial"))'
    )
  );

COMMENT ON COLUMN methods.animal_procedures_avoided IS
  'JSON array of animal procedures replaced/reduced/refined: '
  '{name, species (species.slug), oecd_ref, r_type, extent (total|partial, required for replacement)}.';

-- Rabbit pyrogen test --------------------------------------------------------
UPDATE methods SET animal_procedures_avoided = '[
  {"name": {"en-us": "Rabbit pyrogen test", "pt-br": "Teste de pirogênio em coelhos"},
   "species": "rabbit", "oecd_ref": null, "r_type": "replacement", "extent": "total"}
]'::jsonb WHERE id = 20;

UPDATE methods SET animal_procedures_avoided = '[
  {"name": {"en-us": "Rabbit pyrogen test", "pt-br": "Teste de pirogênio em coelhos"},
   "species": "rabbit", "oecd_ref": null, "r_type": "replacement", "extent": "partial"}
]'::jsonb WHERE id = 38;

UPDATE methods SET animal_procedures_avoided = '[
  {"name": {"en-us": "Use of horseshoe crab lysate (LAL)", "pt-br": "Uso de lisado de caranguejo-ferradura (LAL)"},
   "species": "horseshoe_crab", "oecd_ref": null, "r_type": "replacement", "extent": "total"}
]'::jsonb WHERE id = 56;

-- Rabies: mouse inoculation test ---------------------------------------------
UPDATE methods SET animal_procedures_avoided = '[
  {"name": {"en-us": "Mouse inoculation test (MIT)", "pt-br": "Teste de inoculação em camundongos (MIT)"},
   "species": "mouse", "oecd_ref": null, "r_type": "replacement", "extent": "partial"}
]'::jsonb WHERE id IN (30, 33, 34, 35);

-- Acute oral toxicity ----------------------------------------------------------
UPDATE methods SET animal_procedures_avoided = '[
  {"name": {"en-us": "In vivo acute oral toxicity tests (LD50 determination)", "pt-br": "Testes de toxicidade oral aguda in vivo (determinação da DL50)"},
   "species": null, "oecd_ref": null, "r_type": "reduction", "extent": null},
  {"name": {"en-us": "In vivo acute oral toxicity tests (LD50 determination)", "pt-br": "Testes de toxicidade oral aguda in vivo (determinação da DL50)"},
   "species": null, "oecd_ref": null, "r_type": "replacement", "extent": "partial"}
]'::jsonb WHERE id = 22;

UPDATE methods SET animal_procedures_avoided = '[
  {"name": {"en-us": "Traditional LD50 acute oral toxicity test", "pt-br": "Teste tradicional de toxicidade oral aguda (DL50)"},
   "species": null, "oecd_ref": null, "r_type": "reduction", "extent": null},
  {"name": {"en-us": "Traditional LD50 acute oral toxicity test", "pt-br": "Teste tradicional de toxicidade oral aguda (DL50)"},
   "species": null, "oecd_ref": null, "r_type": "refinement", "extent": null}
]'::jsonb WHERE id = 23;

UPDATE methods SET animal_procedures_avoided = '[
  {"name": {"en-us": "Conventional acute oral toxicity tests", "pt-br": "Testes convencionais de toxicidade aguda oral"},
   "species": null, "oecd_ref": null, "r_type": "reduction", "extent": null}
]'::jsonb WHERE id = 24;

-- Combined study ---------------------------------------------------------------
UPDATE methods SET animal_procedures_avoided = '[
  {"name": {"en-us": "Separate repeated-dose and reproductive/developmental toxicity studies", "pt-br": "Estudos separados de toxicidade por doses repetidas e de toxicidade reprodutiva ou do desenvolvimento"},
   "species": null, "oecd_ref": null, "r_type": "reduction", "extent": null}
]'::jsonb WHERE id = 37;

-- Fish embryo test ---------------------------------------------------------------
UPDATE methods SET animal_procedures_avoided = '[
  {"name": {"en-us": "Acute toxicity tests on juvenile or adult fish", "pt-br": "Testes de toxicidade aguda em peixes juvenis ou adultos"},
   "species": null, "oecd_ref": null, "r_type": "replacement", "extent": "partial"}
]'::jsonb WHERE id = 53;

COMMIT;
