-- =============================================================================
-- Migration 072: parent endpoints carry the union of their descendants'
-- external_oht_codes (as already done for 4.0, 4.1, 2.4, 2.5).
--
-- Filled (were empty): 2.0 Human health effects, 2.2 Systemic toxicity,
-- 2.6 Other health effects.
-- Completed: 1.0 / 1.1 (+59 Dermal absorption), 2.1 / 2.1.1 (+66-3 In vitro
-- phototoxicity), 3.0 (+66-3, 75-2), 3.1 (+75-2).
-- All codes are templates listed in the OHT table.
-- =============================================================================

BEGIN;

UPDATE endpoints e
SET external_oht_codes = v.codes::jsonb
FROM (VALUES
  ('1.0',  '["58","59"]'),
  ('1.1',  '["58","59"]'),
  ('2.0',  '["60","61","62","63","64","65","66-1","66-3","67","68","69-1","69-2","70","71","72","73","74","76","77","78"]'),
  ('2.1',  '["64","65","66-3"]'),
  ('2.1.1','["64","66-3"]'),
  ('2.2',  '["60","61","62","63","67","68","69-1","69-2"]'),
  ('2.6',  '["72","76","77","78"]'),
  ('3.0',  '["66-3","75-2","78","201"]'),
  ('3.1',  '["75-2","78","201"]')
) AS v(code, codes)
WHERE e.code = v.code;

COMMIT;
