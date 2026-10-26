-- =============================================================================
-- Migration 082: species vocabulary (review plan, section 7).
-- Used by method_materials.species_id and, by slug, in
-- methods.animal_procedures_avoided.
-- =============================================================================

BEGIN;

CREATE TABLE species (
  id SERIAL PRIMARY KEY,
  slug TEXT NOT NULL UNIQUE,
  scientific_name TEXT,
  name JSONB NOT NULL,                       -- {"en-us": "...", "pt-br": "..."}
  taxon_group TEXT,                          -- mammal | bird | fish | invertebrate | microorganism
  is_vertebrate BOOLEAN,
  sort_order INTEGER NOT NULL DEFAULT 0,
  active BOOLEAN NOT NULL DEFAULT TRUE,
  created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

COMMENT ON TABLE species IS 'Controlled vocabulary of species (animal or cell source).';

INSERT INTO species (slug, scientific_name, name, taxon_group, is_vertebrate, sort_order) VALUES
  ('human',          'Homo sapiens',               '{"en-us": "Human", "pt-br": "Humano"}',                         'mammal',       TRUE,  1),
  ('rat',            'Rattus norvegicus',          '{"en-us": "Rat", "pt-br": "Rato"}',                             'mammal',       TRUE,  2),
  ('mouse',          'Mus musculus',               '{"en-us": "Mouse", "pt-br": "Camundongo"}',                     'mammal',       TRUE,  3),
  ('rabbit',         'Oryctolagus cuniculus',      '{"en-us": "Rabbit", "pt-br": "Coelho"}',                        'mammal',       TRUE,  4),
  ('guinea_pig',     'Cavia porcellus',            '{"en-us": "Guinea pig", "pt-br": "Cobaia"}',                    'mammal',       TRUE,  5),
  ('dog',            'Canis lupus familiaris',     '{"en-us": "Dog", "pt-br": "Cão"}',                              'mammal',       TRUE,  6),
  ('bovine',         'Bos taurus',                 '{"en-us": "Bovine", "pt-br": "Bovino"}',                        'mammal',       TRUE,  7),
  ('chicken',        'Gallus gallus domesticus',   '{"en-us": "Chicken", "pt-br": "Galinha"}',                      'bird',         TRUE,  8),
  ('zebrafish',      'Danio rerio',                '{"en-us": "Zebrafish", "pt-br": "Paulistinha (zebrafish)"}',    'fish',         TRUE,  9),
  ('rainbow_trout',  'Oncorhynchus mykiss',        '{"en-us": "Rainbow trout", "pt-br": "Truta arco-íris"}',        'fish',         TRUE,  10),
  ('horseshoe_crab', 'Limulus polyphemus',         '{"en-us": "Horseshoe crab", "pt-br": "Caranguejo-ferradura"}',  'invertebrate', FALSE, 11);

COMMIT;
