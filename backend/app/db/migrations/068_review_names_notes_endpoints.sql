-- =============================================================================
-- Migration 068: review of method names, regulation notes and endpoints
-- (checked against the source PDFs in docs/oecd_files).
--
-- 1. regulations.notes: drop the "Jurisdiction 'both' via RN 37/2018" claim
--    (CONCEA RN 37/2018 is the euthanasia guideline, not an OECD TG
--    equivalence rule) and replace stale "not confirmed / verify" notes with
--    the resolution that recognises the method (RN 31/2016, RN 56/2022).
-- 2. methods.name: remove the leading "Test No. XXX:" / "OECD TG XXX:" prefix
--    (the TG number is kept in methods.oecd_ref).
-- 3. endpoints:
--    - TG 473 (chromosomal aberration): add 22 (Genotoxicity), as TG 487.
--    - TG 456 Brazil regulation (RN 56/2022 "Efeitos endócrinos"): 32 -> 36,
--      matching methods.endpoints and the OECD row.
--    - MAT (Farmacopeia Brasileira): add 51 (Non-endotoxin pyrogens).
-- =============================================================================

BEGIN;

-- 1. notes ---------------------------------------------------------------
UPDATE regulations SET notes = 'Recognized via CONCEA RN 18/2014, Art. 2, I-d.'
WHERE id IN (1, 2);

UPDATE regulations SET notes = 'Recognized via CONCEA RN 31/2016, Art. 2, I-b.'
WHERE id = 17;

UPDATE regulations SET notes = 'Recognized via CONCEA RN 31/2016, Art. 2, II-a.'
WHERE id = 18;

UPDATE regulations SET notes = 'Recognized via CONCEA RN 31/2016, Art. 2, II-b.'
WHERE id = 19;

UPDATE regulations SET notes = 'Recognized via CONCEA RN 56/2022, Art. 2, I-5-a.'
WHERE id = 29;

UPDATE regulations SET notes = 'Recognized via CONCEA RN 56/2022, Art. 2, I-5-c.'
WHERE id IN (31, 32);

-- 2. method names --------------------------------------------------------
UPDATE methods
SET name = jsonb_build_object(
  'en-us', regexp_replace(name->>'en-us', '^(OECD )?(Test No\.|TG) ?[0-9]+[A-E]?: ?', ''),
  'pt-br', regexp_replace(name->>'pt-br', '^(OECD |OCDE )?(Test No\.|Teste No\.|Teste Nº|Teste nº|Teste OCDE No\.|TG) ?[0-9]+[A-E]?: ?', '')
)
WHERE name->>'en-us' ~ '^(OECD )?(Test No\.|TG) ?[0-9]+[A-E]?: '
   OR name->>'pt-br' ~ '^(OECD |OCDE )?(Test No\.|Teste No\.|Teste Nº|Teste nº|Teste OCDE No\.|TG) ?[0-9]+[A-E]?: ';

-- 3. endpoints -----------------------------------------------------------
UPDATE methods SET endpoints = ARRAY[22, 23]
WHERE oecd_ref = 'TG 473' AND endpoints = ARRAY[23];

UPDATE regulations SET regulatory_endpoints = ARRAY[36]
WHERE id = 67 AND regulatory_endpoints = ARRAY[32];

UPDATE methods SET endpoints = ARRAY[48, 51]
WHERE id = 20 AND endpoints = ARRAY[48];

COMMIT;
