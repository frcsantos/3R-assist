-- =============================================================================
-- Migration 096: LAL (method 38) checked against the Farmacopeia Brasileira,
-- 7th ed., vol. I, MG 5.5.2.7.3-02 "Teste de endotoxinas bacterianas"
-- (scanned PDF, read by OCR). The reagent is the aqueous extract of circulating
-- amebocytes of Limulus polyphemus or Tachypleus tridentatus; the chapter
-- describes gel-clot, turbidimetric and chromogenic techniques and says
-- nothing about the rabbit pyrogen test or about the 3Rs.
-- =============================================================================

BEGIN;

INSERT INTO species (slug, scientific_name, name, taxon_group, is_vertebrate, sort_order) VALUES
  ('tachypleus_tridentatus', 'Tachypleus tridentatus',
   '{"en-us": "Tri-spine horseshoe crab", "pt-br": "Caranguejo-ferradura asiático"}', 'invertebrate', FALSE, 15);

UPDATE method_materials
SET name = '{"en-us": "Amebocyte lysate (LAL) from Limulus polyphemus", "pt-br": "Lisado de amebócitos (LAL) de Limulus polyphemus"}'::jsonb,
    notes = 'Farmacopeia Brasileira 7a ed., MG 5.5.2.7.3-02: aqueous extract of circulating amebocytes of Limulus polyphemus or Tachypleus tridentatus'
WHERE method_id = 38 AND kind = 'biological_extract';

INSERT INTO method_materials (method_id, kind, name, species_id, origin, animal_derived, notes)
VALUES (38, 'biological_extract',
        '{"en-us": "Amebocyte lysate (LAL) from Tachypleus tridentatus", "pt-br": "Lisado de amebócitos (LAL) de Tachypleus tridentatus"}'::jsonb,
        (SELECT id FROM species WHERE slug = 'tachypleus_tridentatus'), 'animal', TRUE,
        'Farmacopeia Brasileira 7a ed., MG 5.5.2.7.3-02: alternative source species of the LAL reagent');

COMMIT;
