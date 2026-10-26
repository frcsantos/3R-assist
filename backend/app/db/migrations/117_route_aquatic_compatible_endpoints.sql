-- =============================================================================
-- Migration 117: aquatic-waterborne route compatible with the children of 4.1.
-- compatible_endpoints listed only the parent (39, Aquatic effects), while
-- methods use the specific endpoints (41 Fish toxicity for TG 212 / TG 236).
-- Adds 40-43 (aquatic toxicity, fish, invertebrates, algae/plants).
-- =============================================================================

BEGIN;

UPDATE routes
SET compatible_endpoints = ARRAY[39, 40, 41, 42, 43]
WHERE slug = 'aquatic-waterborne'
  AND compatible_endpoints = ARRAY[39];

COMMIT;
