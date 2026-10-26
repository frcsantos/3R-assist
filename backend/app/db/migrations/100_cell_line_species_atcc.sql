-- =============================================================================
-- Migration 100: species of U937 and Neuro-2a confirmed in the ATCC catalogue.
--   CRL-1593.2 U-937: Homo sapiens (human), pleural effusion, histiocytic
--     lymphoma, monocyte (https://www.atcc.org/products/crl-1593.2).
--   CCL-131 Neuro-2a: Mus musculus (mouse), brain, neuroblastoma, neuroblast
--     (https://www.atcc.org/products/ccl-131).
-- =============================================================================

BEGIN;

UPDATE method_materials
SET species_id = (SELECT id FROM species WHERE slug = 'human'), origin = 'human',
    notes = 'TG 442E text (U937 cell line); ATCC CRL-1593.2: Homo sapiens (human), histiocytic lymphoma, monocyte'
WHERE method_id = 12 AND name->>'en-us' = 'U937 cells (U-SENS)';

UPDATE method_materials
SET species_id = (SELECT id FROM species WHERE slug = 'mouse'), origin = 'animal',
    notes = 'WOAH 3.1.19: neuroblastoma cells such as N2a (ATCC CCL-131); ATCC CCL-131 Neuro-2a: Mus musculus (mouse), brain neuroblastoma'
WHERE method_id = 34 AND kind = 'cell_line';

COMMIT;
