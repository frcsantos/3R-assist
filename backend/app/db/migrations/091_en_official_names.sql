-- =============================================================================
-- Migration 091: English method names aligned with the official title of the
-- source document (review plan), only where this does not conflict with the
-- Portuguese name taken from regulations.regulatory_quote.
--   TG 430, 437, 429, 491: title from the OECD guideline.
--   rFC: title of Ph. Eur. 2.6.32, which Res. CONCEA 77/2026 cites in English.
--   DFA, dRIT, RTCIT: English terms cited in Res. CONCEA 75/2026.
-- Not changed (conflict or no source in the repository): GD 129, TG 442A,
-- TG 442D/E, MAT, LAL, RT-PCR.
-- =============================================================================

BEGIN;

UPDATE methods m
SET name = jsonb_set(m.name, '{en-us}', to_jsonb(v.en::text))
FROM (VALUES
  (4,  'In Vitro Skin Corrosion: Transcutaneous Electrical Resistance Test Method (TER)'),
  (6,  'Bovine Corneal Opacity and Permeability Test Method for Identifying i) Chemicals Inducing Serious Eye Damage and ii) Chemicals Not Requiring Classification for Eye Irritation or Serious Eye Damage'),
  (13, 'Skin Sensitisation: Local Lymph Node Assay'),
  (40, 'Short Time Exposure In Vitro Test Method for Identifying i) Chemicals Inducing Serious Eye Damage and ii) Chemicals Not Requiring Classification for Eye Irritation or Serious Eye Damage'),
  (56, 'Test for bacterial endotoxins using recombinant factor C'),
  (30, 'Direct Fluorescent Antibody Test - DFA Test'),
  (33, 'Direct Rapid Immunohistochemistry Test - dRIT'),
  (34, 'Rabies Tissue Culture Infection Test - RTCIT')
) AS v(id, en)
WHERE m.id = v.id;

COMMIT;
