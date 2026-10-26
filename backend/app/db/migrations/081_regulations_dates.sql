-- =============================================================================
-- Migration 081: publication / effective dates and replacement term on
-- regulations (review plan: "data limite para a substituição").
--
-- regulatory_date keeps the date of the act (signature). Added:
--   published_date          publication in the Diário Oficial da União
--   effective_date          entry into force
--   replacement_term_years  term (years) to replace the original method, when
--                           the resolution sets one (5 years in the CONCEA RNs)
--   replacement_deadline    effective_date + term (generated)
-- Filled for the Brazilian rows from the resolution texts in docs/oecd_files.
-- RN 45/2019 sets no term (published 22/10/2019, in force on publication).
-- OECD rows are left empty.
-- =============================================================================

BEGIN;

ALTER TABLE regulations
  ADD COLUMN published_date DATE,
  ADD COLUMN effective_date DATE,
  ADD COLUMN replacement_term_years SMALLINT
    CHECK (replacement_term_years IS NULL OR replacement_term_years > 0);

ALTER TABLE regulations
  ADD COLUMN replacement_deadline DATE
  GENERATED ALWAYS AS (
    (effective_date + make_interval(years => replacement_term_years::int))::date
  ) STORED;

COMMENT ON COLUMN regulations.published_date IS 'Publication date in the official gazette (DOU).';
COMMENT ON COLUMN regulations.effective_date IS 'Date the act enters into force.';
COMMENT ON COLUMN regulations.replacement_term_years IS 'Years allowed to replace the original method, when the act sets a term.';
COMMENT ON COLUMN regulations.replacement_deadline IS 'effective_date + replacement_term_years (generated).';

UPDATE regulations r
SET published_date = v.pub::date,
    effective_date = v.eff::date,
    replacement_term_years = v.term
FROM (VALUES
  (4, '2014-09-25', '2014-09-25', 5),   -- RN 18/2014
  (3, '2016-08-19', '2016-08-19', 5),   -- RN 31/2016
  (2, '2019-10-22', '2019-10-22', NULL::int), -- RN 45/2019 (no term)
  (5, '2022-10-07', '2022-11-01', 5),   -- RN 56/2022 (in force 1 Nov 2022)
  (8, '2026-01-23', '2026-01-23', 5),   -- Res. CONCEA 75/2026
  (7, '2026-02-09', '2026-02-09', 5),   -- Res. CONCEA 76/2026
  (6, '2026-07-23', '2026-07-23', 5)    -- Res. CONCEA 77/2026
) AS v(doc_id, pub, eff, term)
WHERE r.regulatory_doc_id = v.doc_id
  AND r.jurisdiction->>'en-us' = 'Brazil';

COMMIT;
