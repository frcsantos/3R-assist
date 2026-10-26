-- =============================================================================
-- Migration 115: enum_terms — localized labels for coded (enum-like) columns.
-- The codes stay in their columns (and CHECK constraints); the labels used to
-- live only in the frontend locale files. GET /vocabularies/enums serves them.
--   domain             column
--   animal_use         methods.animal_use
--   test_system        methods.test_system[]
--   review_status      methods.review_status
--   validation_status  methods.validation_status
--   regulatory_status  regulations.regulatory_status
--   material_kind      method_materials.kind
--   material_origin    method_materials.origin
--   extent             methods.animal_procedures_avoided[].extent
--   three_r_type       methods.animal_procedures_avoided[].r_type
--   document_category  documents.categories[]
--   taxon_group        species.taxon_group
-- =============================================================================

BEGIN;

CREATE TABLE IF NOT EXISTS enum_terms (
  domain      TEXT    NOT NULL CHECK (domain ~ '^[a-z][a-z0-9_]*$'),
  code        TEXT    NOT NULL,
  name        JSONB   NOT NULL,
  description JSONB   NOT NULL DEFAULT '{"en-us":"","pt-br":""}'::jsonb,
  sort_order  INTEGER NOT NULL DEFAULT 0,
  active      BOOLEAN NOT NULL DEFAULT TRUE,
  PRIMARY KEY (domain, code),
  CHECK (name ? 'en-us' AND name ? 'pt-br')
);

COMMENT ON TABLE enum_terms IS
  'Localized labels for coded columns; domain names the owning column (see migration 115).';

INSERT INTO enum_terms (domain, code, name, sort_order) VALUES
  ('animal_use', 'none', '{"en-us": "None", "pt-br": "Nenhum"}'::jsonb, 1),
  ('animal_use', 'animal_derived_material', '{"en-us": "Animal-derived material", "pt-br": "Material derivado de animal"}'::jsonb, 2),
  ('animal_use', 'slaughterhouse_byproduct', '{"en-us": "Slaughterhouse byproduct", "pt-br": "Subproduto de abatedouro"}'::jsonb, 3),
  ('animal_use', 'animals_killed_for_tissue', '{"en-us": "Animals killed for tissue", "pt-br": "Animais sacrificados para tecido"}'::jsonb, 4),
  ('animal_use', 'live_animals', '{"en-us": "Live animals", "pt-br": "Animais vivos"}'::jsonb, 5),
  ('animal_use', 'mixed_or_variable', '{"en-us": "Mixed or variable", "pt-br": "Misto ou variável"}'::jsonb, 6),
  ('test_system', 'in_silico', '{"en-us": "In silico", "pt-br": "In silico"}'::jsonb, 1),
  ('test_system', 'in_chemico', '{"en-us": "In chemico", "pt-br": "In chemico"}'::jsonb, 2),
  ('test_system', 'in_data', '{"en-us": "In data", "pt-br": "In data"}'::jsonb, 3),
  ('test_system', 'in_vitro', '{"en-us": "In vitro", "pt-br": "In vitro"}'::jsonb, 4),
  ('test_system', 'ex_vivo', '{"en-us": "Ex vivo", "pt-br": "Ex vivo"}'::jsonb, 5),
  ('test_system', 'in_vivo', '{"en-us": "In vivo", "pt-br": "In vivo"}'::jsonb, 6),
  ('test_system', 'unclear', '{"en-us": "Unclear", "pt-br": "Incerto"}'::jsonb, 7),
  ('review_status', 'not_reviewed', '{"en-us": "Not reviewed", "pt-br": "Não revisado"}'::jsonb, 1),
  ('review_status', 'in_review', '{"en-us": "In review", "pt-br": "Em revisão"}'::jsonb, 2),
  ('review_status', 'reviewed', '{"en-us": "Reviewed", "pt-br": "Revisado"}'::jsonb, 3),
  ('material_kind', 'cell_line', '{"en-us": "Cell line", "pt-br": "Linhagem celular"}'::jsonb, 1),
  ('material_kind', 'primary_cells', '{"en-us": "Primary cells", "pt-br": "Células primárias"}'::jsonb, 2),
  ('material_kind', 'tissue', '{"en-us": "Tissue", "pt-br": "Tecido"}'::jsonb, 3),
  ('material_kind', 'reconstructed_tissue', '{"en-us": "Reconstructed tissue", "pt-br": "Tecido reconstruído"}'::jsonb, 4),
  ('material_kind', 'organoid', '{"en-us": "Organoid", "pt-br": "Organoide"}'::jsonb, 5),
  ('material_kind', 'embryo', '{"en-us": "Embryo", "pt-br": "Embrião"}'::jsonb, 6),
  ('material_kind', 'whole_organism', '{"en-us": "Whole organism", "pt-br": "Organismo inteiro"}'::jsonb, 7),
  ('material_kind', 'subcellular_fraction', '{"en-us": "Subcellular fraction", "pt-br": "Fração subcelular"}'::jsonb, 8),
  ('material_kind', 'biological_extract', '{"en-us": "Biological extract", "pt-br": "Extrato biológico"}'::jsonb, 9),
  ('material_kind', 'recombinant_protein', '{"en-us": "Recombinant protein", "pt-br": "Proteína recombinante"}'::jsonb, 10),
  ('material_kind', 'synthetic_reagent', '{"en-us": "Synthetic reagent", "pt-br": "Reagente sintético"}'::jsonb, 11),
  ('material_kind', 'sample', '{"en-us": "Sample", "pt-br": "Amostra"}'::jsonb, 12),
  ('material_kind', 'computational', '{"en-us": "Computational", "pt-br": "Computacional"}'::jsonb, 13),
  ('material_kind', 'culture_supplement', '{"en-us": "Culture supplement", "pt-br": "Suplemento de cultura"}'::jsonb, 14),
  ('material_kind', 'metabolic_activation', '{"en-us": "Metabolic activation", "pt-br": "Ativação metabólica"}'::jsonb, 15),
  ('material_kind', 'matrix', '{"en-us": "Matrix", "pt-br": "Matriz"}'::jsonb, 16),
  ('extent', 'total', '{"en-us": "total", "pt-br": "total"}'::jsonb, 1),
  ('extent', 'partial', '{"en-us": "partial", "pt-br": "parcial"}'::jsonb, 2),
  ('validation_status', 'recognized', '{"en-us": "Recognized", "pt-br": "Reconhecido"}'::jsonb, 1),
  ('validation_status', 'under_validation', '{"en-us": "Under validation", "pt-br": "Em validação"}'::jsonb, 2),
  ('validation_status', 'validated', '{"en-us": "Validated", "pt-br": "Validado"}'::jsonb, 3),
  ('validation_status', 'partially_validated', '{"en-us": "Partially validated", "pt-br": "Parcialmente validado"}'::jsonb, 4),
  ('validation_status', 'not_validated', '{"en-us": "Not validated", "pt-br": "Não validado"}'::jsonb, 5),
  ('validation_status', 'unclear', '{"en-us": "Unclear", "pt-br": "Incerto"}'::jsonb, 6),
  ('regulatory_status', 'not_approved', '{"en-us": "Not approved", "pt-br": "Não aprovado"}'::jsonb, 1),
  ('regulatory_status', 'approved', '{"en-us": "Approved", "pt-br": "Aprovado"}'::jsonb, 2),
  ('regulatory_status', 'recognized', '{"en-us": "Recognized", "pt-br": "Reconhecido"}'::jsonb, 3),
  ('regulatory_status', 'recommended', '{"en-us": "Recommended", "pt-br": "Recomendado"}'::jsonb, 4),
  ('regulatory_status', 'mandatory', '{"en-us": "Mandatory", "pt-br": "Obrigatório"}'::jsonb, 5),
  ('three_r_type', 'replacement', '{"en-us": "Replacement", "pt-br": "Substituição"}'::jsonb, 1),
  ('three_r_type', 'reduction', '{"en-us": "Reduction", "pt-br": "Redução"}'::jsonb, 2),
  ('three_r_type', 'refinement', '{"en-us": "Refinement", "pt-br": "Refinamento"}'::jsonb, 3),
  ('document_category', 'method_protocol', '{"en-us": "Method protocol", "pt-br": "Protocolo de método"}'::jsonb, 1),
  ('document_category', 'guideline', '{"en-us": "Guideline", "pt-br": "Diretriz"}'::jsonb, 2),
  ('document_category', 'regulation', '{"en-us": "Regulation", "pt-br": "Regulamento"}'::jsonb, 3),
  ('document_category', 'other', '{"en-us": "Other", "pt-br": "Outro"}'::jsonb, 4),
  ('material_origin', 'human', '{"en-us": "Human", "pt-br": "Humana"}'::jsonb, 1),
  ('material_origin', 'animal', '{"en-us": "Animal", "pt-br": "Animal"}'::jsonb, 2),
  ('material_origin', 'recombinant', '{"en-us": "Recombinant", "pt-br": "Recombinante"}'::jsonb, 3),
  ('material_origin', 'microbial', '{"en-us": "Microbial", "pt-br": "Microbiana"}'::jsonb, 4),
  ('material_origin', 'synthetic', '{"en-us": "Synthetic", "pt-br": "Sintética"}'::jsonb, 5),
  ('taxon_group', 'mammal', '{"en-us": "Mammal", "pt-br": "Mamífero"}'::jsonb, 1),
  ('taxon_group', 'bird', '{"en-us": "Bird", "pt-br": "Ave"}'::jsonb, 2),
  ('taxon_group', 'fish', '{"en-us": "Fish", "pt-br": "Peixe"}'::jsonb, 3),
  ('taxon_group', 'invertebrate', '{"en-us": "Invertebrate", "pt-br": "Invertebrado"}'::jsonb, 4),
  ('taxon_group', 'microorganism', '{"en-us": "Microorganism", "pt-br": "Microrganismo"}'::jsonb, 5)
ON CONFLICT (domain, code) DO NOTHING;

COMMIT;
