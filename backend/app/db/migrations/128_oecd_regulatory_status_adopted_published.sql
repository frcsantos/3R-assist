-- =============================================================================
-- Migration 128: regulatory status of the OECD rows.
--   - regulations.regulatory_status accepts `adopted` and `published`.
--   - OECD Test Guidelines (TG) -> `adopted`; the OECD Guidance Document
--     (GD 129, method 22) -> `published`.
--   - CONCEA rows (Brazil) are not touched.
-- =============================================================================

BEGIN;

ALTER TABLE regulations DROP CONSTRAINT IF EXISTS regulations_regulatory_status_check;
ALTER TABLE regulations
  ADD CONSTRAINT regulations_regulatory_status_check CHECK (
    regulatory_status IS NULL
    OR regulatory_status IN (
      'not_approved', 'approved', 'recognized', 'adopted', 'published',
      'recommended', 'mandatory'
    )
  );

INSERT INTO enum_terms (domain, code, name, sort_order) VALUES
  ('regulatory_status', 'adopted',   '{"en-us": "Adopted", "pt-br": "Adotado"}'::jsonb,     6),
  ('regulatory_status', 'published', '{"en-us": "Published", "pt-br": "Publicado"}'::jsonb, 7)
ON CONFLICT (domain, code) DO NOTHING;

UPDATE regulations
SET regulatory_status = 'adopted'
WHERE jurisdiction->>'en-us' = 'OECD'
  AND method_id <> 22;

UPDATE regulations
SET regulatory_status = 'published'
WHERE jurisdiction->>'en-us' = 'OECD'
  AND method_id = 22;

COMMIT;
