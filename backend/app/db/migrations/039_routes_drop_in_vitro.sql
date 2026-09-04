-- =============================================================================
-- Migration 039: remove routes.in_vitro (use methods.test_system instead)
-- =============================================================================

BEGIN;

-- Drop compatibility rows first.
DELETE FROM route_endpoints
WHERE route_code = 'in_vitro';

-- Strip in_vitro from methods.routes_applicable arrays.
UPDATE methods
SET
  routes_applicable = (
    SELECT COALESCE(jsonb_agg(elem ORDER BY ordinality), '[]'::jsonb)
    FROM jsonb_array_elements_text(routes_applicable)
      WITH ORDINALITY AS t(elem, ordinality)
    WHERE elem <> 'in_vitro'
  ),
  updated_at = NOW()
WHERE routes_applicable IS NOT NULL
  AND routes_applicable @> '"in_vitro"'::jsonb;

-- Empty arrays → NULL (route-agnostic), matching prior semantics.
UPDATE methods
SET
  routes_applicable = NULL,
  updated_at = NOW()
WHERE routes_applicable = '[]'::jsonb;

DELETE FROM routes
WHERE code = 'in_vitro';

COMMIT;
