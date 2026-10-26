-- =============================================================================
-- Migration 088: species used by the bacterial reverse mutation test and new
-- method_materials kinds for animal-derived inputs that decide animal_use
-- (culture supplements such as serum, metabolic activation systems such as S9,
-- and protein/collagen matrices).
-- =============================================================================

BEGIN;

INSERT INTO species (slug, scientific_name, name, taxon_group, is_vertebrate, sort_order) VALUES
  ('salmonella_typhimurium', 'Salmonella typhimurium', '{"en-us": "Salmonella typhimurium", "pt-br": "Salmonella typhimurium"}', 'microorganism', FALSE, 12),
  ('escherichia_coli',       'Escherichia coli',       '{"en-us": "Escherichia coli", "pt-br": "Escherichia coli"}',             'microorganism', FALSE, 13);

ALTER TABLE method_materials DROP CONSTRAINT IF EXISTS method_materials_kind_check;
ALTER TABLE method_materials
  ADD CONSTRAINT method_materials_kind_check CHECK (kind IN (
    'cell_line', 'primary_cells', 'tissue', 'reconstructed_tissue', 'organoid',
    'embryo', 'whole_organism', 'subcellular_fraction', 'biological_extract',
    'recombinant_protein', 'synthetic_reagent', 'sample', 'computational',
    'culture_supplement', 'metabolic_activation', 'matrix'
  ));

COMMIT;
