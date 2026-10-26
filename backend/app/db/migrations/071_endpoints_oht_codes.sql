-- =============================================================================
-- Migration 071: reconcile endpoints.external_oht_codes with the OECD
-- Harmonised Templates (OHT) list.
--
-- 1. Add missing templates: Neurotoxicity (76) to endpoint 2.6.2, Immunotoxicity
--    (77) to 2.6.3, Sediment toxicity (49) to 4.3.
-- 2. Remove generic codes 78 (Specific investigations: other studies) and
--    201 (Intermediate effects) from the specific endpoints that already have
--    a dedicated template: phototoxicity (2.1.1.3), photoreactivity (3.2) and
--    estrogenic / androgenic / steroidogenesis activity (3.1.1, 3.1.2, 3.1.4).
--    Endpoints 3.1 and 3.1.3 (no dedicated template) keep their codes.
-- =============================================================================

BEGIN;

UPDATE endpoints SET external_oht_codes = '["76","78"]'::jsonb WHERE code = '2.6.2' AND external_oht_codes = '["78"]'::jsonb;
UPDATE endpoints SET external_oht_codes = '["77","78"]'::jsonb WHERE code = '2.6.3' AND external_oht_codes = '["78"]'::jsonb;
UPDATE endpoints SET external_oht_codes = '["49"]'::jsonb      WHERE code = '4.3'   AND external_oht_codes = '[]'::jsonb;

UPDATE endpoints SET external_oht_codes = '["66-3"]'::jsonb WHERE code IN ('2.1.1.3', '3.2');
UPDATE endpoints SET external_oht_codes = '["75-2"]'::jsonb WHERE code IN ('3.1.1', '3.1.2', '3.1.4');

COMMIT;
