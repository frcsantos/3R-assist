-- Migration 073: complete 072 for the top-level endpoints, whose codes are
-- stored as '1', '2', '3' (not '1.0', '2.0', '3.0').
BEGIN;

UPDATE endpoints e
SET external_oht_codes = v.codes::jsonb
FROM (VALUES
  ('1', '["58","59"]'),
  ('2', '["60","61","62","63","64","65","66-1","66-3","67","68","69-1","69-2","70","71","72","73","74","76","77","78"]'),
  ('3', '["66-3","75-2","78","201"]')
) AS v(code, codes)
WHERE e.code = v.code;

COMMIT;
