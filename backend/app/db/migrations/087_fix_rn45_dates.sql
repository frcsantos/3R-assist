-- =============================================================================
-- Migration 087: correct the dates and replacement term of RN 45/2019 (MAT).
-- The resolution is dated 22/10/2019 (regulatory_date) but was published in
-- the DOU of 25/10/2019 (Seção 1, nº 208); art. 5 puts it in force on
-- publication and art. 4, single paragraph, sets a 5-year term to replace the
-- original method. Migration 081 had 22/10/2019 and no term.
-- =============================================================================

BEGIN;

UPDATE regulations
SET published_date = '2019-10-25',
    effective_date = '2019-10-25',
    replacement_term_years = 5
WHERE regulatory_doc_id = 2
  AND jurisdiction->>'en-us' = 'Brazil';

COMMIT;
