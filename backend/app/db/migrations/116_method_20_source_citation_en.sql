-- =============================================================================
-- Migration 116: method 20 (Monocyte Activation Test) source_citation had only
-- a pt-br value (with a double space after "MONÓCITOS."). Collapse the double
-- space and add the en-us value. source_citation is a TEXT column holding JSON.
-- =============================================================================

BEGIN;

UPDATE methods
SET source_citation = jsonb_build_object(
      'en-us',
      '5.5.2.7.1 MONOCYTE ACTIVATION TEST. Farmacopeia Brasileira, 7th edition: volume I - RDC version no 940/2024. MG5.5.2.7.1-00.',
      'pt-br',
      regexp_replace(source_citation::jsonb->>'pt-br', ' {2,}', ' ', 'g')
    )::text
WHERE id = 20
  AND source_citation::jsonb ? 'pt-br'
  AND NOT source_citation::jsonb ? 'en-us';

COMMIT;
