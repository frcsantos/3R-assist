-- =============================================================================
-- Migration 083: biological material / system used by each method
-- (review plan, section 6). One row per material.
-- Seeded only with materials stated in the method descriptions or in the
-- summaries of the test guidelines; the remaining methods are for curators.
-- =============================================================================

BEGIN;

CREATE TABLE method_materials (
  id SERIAL PRIMARY KEY,
  method_id INTEGER NOT NULL REFERENCES methods(id) ON DELETE CASCADE,
  kind TEXT NOT NULL CHECK (kind IN (
    'cell_line', 'primary_cells', 'tissue', 'reconstructed_tissue', 'organoid',
    'embryo', 'whole_organism', 'subcellular_fraction', 'biological_extract',
    'recombinant_protein', 'synthetic_reagent', 'sample', 'computational'
  )),
  name JSONB NOT NULL,                         -- {"en-us": "...", "pt-br": "..."}
  species_id INTEGER REFERENCES species(id),
  origin TEXT CHECK (origin IN ('human', 'animal', 'microbial', 'recombinant', 'synthetic', 'none')),
  animal_derived BOOLEAN,                      -- material obtained from animals (cross-check with methods.animal_use)
  notes TEXT,
  created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX idx_method_materials_method ON method_materials (method_id);
CREATE INDEX idx_method_materials_species ON method_materials (species_id);

COMMENT ON TABLE method_materials IS 'Biological material or system used by a method (cells, tissue, organism, reagent).';

INSERT INTO method_materials (method_id, kind, name, species_id, origin, animal_derived, notes)
SELECT v.method_id, v.kind,
       jsonb_build_object('en-us', v.en, 'pt-br', v.pt),
       (SELECT s.id FROM species s WHERE s.slug = v.species),
       v.origin, v.animal_derived, v.notes
FROM (VALUES
  (1,  'reconstructed_tissue', 'Reconstructed human epidermis (RhE)', 'Epiderme humana reconstruída (RhE)', 'human', 'human', NULL::boolean, 'method description'),
  (3,  'reconstructed_tissue', 'Reconstructed human epidermis (RHE)', 'Epiderme humana reconstruída (RHE)', 'human', 'human', NULL, 'method description'),
  (9,  'reconstructed_tissue', 'Reconstructed human cornea-like epithelium (RhCE)', 'Epitélio corneano humano reconstruído (RhCE)', 'human', 'human', NULL, 'method name'),
  (39, 'reconstructed_tissue', 'Reconstructed human cornea-like epithelium (RhCE)', 'Epitélio corneano humano reconstruído (RhCE)', 'human', 'human', NULL, 'method name'),
  (4,  'tissue', 'Rat skin discs', 'Discos de pele de rato', 'rat', 'animal', TRUE, 'TG 430 summary'),
  (6,  'tissue', 'Isolated bovine corneas (cattle slaughtered for commercial purposes)', 'Córneas bovinas isoladas (gado abatido para fins comerciais)', 'bovine', 'animal', TRUE, 'method description'),
  (7,  'tissue', 'Enucleated chicken eyes from slaughterhouses', 'Olhos de frango enucleados de abatedouros', 'chicken', 'animal', TRUE, 'method description'),
  (8,  'cell_line', 'MDCK (Madin-Darby Canine Kidney) cell monolayer', 'Monocamada de células MDCK (Madin-Darby Canine Kidney)', 'dog', 'animal', NULL, 'method description'),
  (16, 'cell_line', 'Balb/c 3T3 cells (murine fibroblast cell line)', 'Células Balb/c 3T3 (linhagem de fibroblastos murinos)', 'mouse', 'animal', NULL, 'method description'),
  (22, 'cell_line', 'BALB/c 3T3 cells', 'Células BALB/c 3T3', 'mouse', 'animal', NULL, 'method description'),
  (22, 'primary_cells', 'Normal human keratinocytes (NHK)', 'Queratinócitos humanos normais (NHK)', 'human', 'human', NULL, 'method description'),
  (40, 'cell_line', 'SIRC cells (Statens Seruminstitut Rabbit Cornea)', 'Células SIRC (Statens Seruminstitut Rabbit Cornea)', 'rabbit', 'animal', NULL, 'TG 491 summary'),
  (54, 'primary_cells', 'Cryopreserved rainbow trout hepatocytes (RT-HEP)', 'Hepatócitos criopreservados de truta arco-íris (RT-HEP)', 'rainbow_trout', 'animal', TRUE, 'TG 319A summary'),
  (55, 'subcellular_fraction', 'Rainbow trout liver S9 fraction (RT-S9)', 'Fração S9 de fígado de truta arco-íris (RT-S9)', 'rainbow_trout', 'animal', TRUE, 'TG 319B summary'),
  (13, 'whole_organism', 'Mouse', 'Camundongo', 'mouse', 'animal', TRUE, 'TG 429 summary'),
  (14, 'whole_organism', 'Mouse (CBA/J strain)', 'Camundongo (linhagem CBA/J)', 'mouse', 'animal', TRUE, 'TG 442A summary'),
  (15, 'whole_organism', 'Mouse', 'Camundongo', 'mouse', 'animal', TRUE, 'TG 442B summary'),
  (23, 'whole_organism', 'Rat (usually females)', 'Rato (normalmente fêmeas)', 'rat', 'animal', TRUE, 'TG 420 summary'),
  (53, 'embryo', 'Zebrafish (Danio rerio) embryos', 'Embriões de zebrafish (Danio rerio)', 'zebrafish', 'animal', TRUE, 'TG 236 summary'),
  (10, 'synthetic_reagent', 'Synthetic model peptides containing lysine or cysteine', 'Peptídeos sintéticos modelo contendo lisina ou cisteína', NULL, 'synthetic', FALSE, 'method description'),
  (38, 'biological_extract', 'Horseshoe crab amebocyte lysate (LAL)', 'Lisado de amebócitos de caranguejo-ferradura (LAL)', 'horseshoe_crab', 'animal', TRUE, 'rFC rationale'),
  (56, 'recombinant_protein', 'Recombinant factor C (rFC)', 'Fator C recombinante (rFC)', NULL, 'recombinant', FALSE, 'method description')
) AS v(method_id, kind, en, pt, species, origin, animal_derived, notes);

COMMIT;
