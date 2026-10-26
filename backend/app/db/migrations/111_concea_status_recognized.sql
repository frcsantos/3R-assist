-- =============================================================================
-- Migration 111: all CONCEA (Brazil) regulations get regulatory_status
-- 'recognized' (the Normative Resolutions recognise the alternative methods;
-- 'approved' stays for the OECD rows). 47 rows, all previously 'approved'.
-- =============================================================================

BEGIN;

UPDATE regulations
SET regulatory_status = 'recognized'
WHERE jurisdiction->>'en-us' = 'Brazil'
  AND regulatory_body->>'en-us' ILIKE 'Conselho Nacional de Controle de Experimenta%';

COMMIT;
