-- =============================================================================
-- Migration 095: rabies methods checked against WOAH Terrestrial Manual 2023,
-- chapter 3.1.19 (Rabies), added to docs/oecd_files.
--  - English names follow the method names of the chapter (DFA, dRIT, RTCIT,
--    pan-lyssavirus RT-PCR); they do not conflict with the Portuguese names of
--    Res. CONCEA 75/2026.
--  - New method_materials kind `antibody` (animal-derived detection reagents).
--  - Materials: CNS tissue from suspect animals; polyclonal or monoclonal
--    antibody conjugates (DFA, dRIT); N2a cells in DMEM with 5% fetal calf
--    serum (RTCIT).
--  - Procedure avoided: the mouse inoculation test (3-4-week-old mice or
--    2-day-old newborn mice, intracerebral); the chapter keeps it as a
--    confirmatory test and says virus isolation in cell culture should replace
--    it wherever possible.
-- =============================================================================

BEGIN;

UPDATE methods m
SET name = jsonb_set(m.name, '{en-us}', to_jsonb(v.en::text))
FROM (VALUES
  (30, 'Direct fluorescent antibody (DFA) test'),
  (33, 'Direct rapid immunohistochemistry test (dRIT)'),
  (34, 'Rabies tissue culture infection test (RTCIT)'),
  (35, 'Pan-lyssavirus reverse-transcription polymerase chain reaction (RT-PCR) assays')
) AS v(id, en)
WHERE m.id = v.id;

ALTER TABLE method_materials DROP CONSTRAINT IF EXISTS method_materials_kind_check;
ALTER TABLE method_materials
  ADD CONSTRAINT method_materials_kind_check CHECK (kind IN (
    'cell_line', 'primary_cells', 'tissue', 'reconstructed_tissue', 'organoid',
    'embryo', 'whole_organism', 'subcellular_fraction', 'biological_extract',
    'recombinant_protein', 'synthetic_reagent', 'sample', 'computational',
    'culture_supplement', 'metabolic_activation', 'matrix', 'antibody'
  ));

UPDATE method_materials SET notes =
  'WOAH 3.1.19: CNS tissue removed from the cranium of suspect animals (brain stem, Ammon''s horn, thalamus, cerebral cortex, cerebellum, medulla oblongata)'
WHERE method_id IN (30, 33, 34, 35) AND kind = 'tissue';

UPDATE method_materials SET notes =
  'WOAH 3.1.19: neuroblastoma cells such as N2a (ATCC CCL-131); species not stated in the chapter'
WHERE method_id = 34 AND kind = 'cell_line';

INSERT INTO method_materials (method_id, kind, name, species_id, origin, animal_derived, notes)
VALUES
  (30, 'antibody',
   '{"en-us": "FITC-labelled polyclonal or monoclonal anti-rabies antibody conjugate", "pt-br": "Conjugado de anticorpo anti-rábico policlonal ou monoclonal marcado com FITC"}'::jsonb,
   NULL, 'animal', NULL, 'WOAH 3.1.19; polyclonal antibodies come from immunised animals, monoclonal ones from hybridomas'),
  (33, 'antibody',
   '{"en-us": "Biotinylated anti-nucleoprotein poly- or monoclonal antibodies (streptavidin-peroxidase detection)", "pt-br": "Anticorpos poli- ou monoclonais anti-nucleoproteína biotinilados (detecção com estreptavidina-peroxidase)"}'::jsonb,
   NULL, 'animal', NULL, 'WOAH 3.1.19; polyclonal antibodies come from immunised animals, monoclonal ones from hybridomas'),
  (34, 'culture_supplement',
   '{"en-us": "5% fetal calf serum in the N2a culture medium (DMEM) and heat-inactivated fetal calf serum in the brain homogenate substrate", "pt-br": "Soro fetal de bezerro a 5% no meio de cultura das células N2a (DMEM) e soro fetal de bezerro inativado no substrato do homogenato de cérebro"}'::jsonb,
   (SELECT id FROM species WHERE slug = 'bovine'), 'animal', TRUE, 'WOAH 3.1.19');

UPDATE methods
SET animal_procedures_avoided = (
  SELECT jsonb_agg(
    e || jsonb_build_object(
      'name', jsonb_build_object(
        'en-us', 'Mouse inoculation test (MIT): intracerebral inoculation of mice',
        'pt-br', 'Teste de inoculação em camundongos (MIT): inoculação intracerebral'),
      'note', jsonb_build_object(
        'en-us', 'WOAH 3.1.19 keeps the MIT as a confirmatory test when primary tests are inconclusive and says virus isolation in cell culture should replace it wherever possible',
        'pt-br', 'O capítulo 3.1.19 da WOAH mantém o MIT como teste confirmatório quando os testes primários são inconclusivos e diz que o isolamento viral em cultura de células deve substituí-lo sempre que possível'))
    ORDER BY ord)
  FROM jsonb_array_elements(animal_procedures_avoided) WITH ORDINALITY AS t(e, ord)
)
WHERE id IN (30, 33, 34, 35);

COMMIT;
