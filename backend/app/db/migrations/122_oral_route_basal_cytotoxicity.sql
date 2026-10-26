-- =============================================================================
-- Migration 122: oral route compatible with basal cytotoxicity (endpoint 58).
-- GD 129 (method 22) uses endpoints 17 (acute systemic toxicity) and 58
-- (basal cytotoxicity) with route 3 (oral), but 58 was in no route's
-- compatible_endpoints. Adds 58 to the oral route.
-- =============================================================================

BEGIN;

UPDATE routes
SET compatible_endpoints = array_append(compatible_endpoints, 58)
WHERE slug = 'oral'
  AND NOT (58 = ANY(compatible_endpoints));

COMMIT;
