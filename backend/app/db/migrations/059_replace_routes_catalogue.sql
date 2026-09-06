-- =============================================================================
-- Migration 059: replace routes catalogue; routes.code → slug
-- Remap methods.routes_applicable dermal → cutaneous; rebuild route_endpoints.
-- =============================================================================

BEGIN;

ALTER TABLE route_endpoints
  DROP CONSTRAINT IF EXISTS route_endpoints_route_code_fkey;

ALTER TABLE routes
  RENAME COLUMN code TO slug;

COMMENT ON COLUMN routes.slug IS
  'URL-safe unique key (hyphenated), e.g. cutaneous, intra-arterial.';

UPDATE methods
SET
  routes_applicable = (
    SELECT COALESCE(jsonb_agg(mapped ORDER BY ordinality), '[]'::jsonb)
    FROM jsonb_array_elements_text(routes_applicable)
      WITH ORDINALITY AS t(elem, ordinality)
    CROSS JOIN LATERAL (
      SELECT CASE
        WHEN elem = 'dermal' THEN 'cutaneous'
        ELSE elem
      END AS mapped
    ) map
  ),
  updated_at = NOW()
WHERE routes_applicable IS NOT NULL;

DELETE FROM route_endpoints;
DELETE FROM routes;

INSERT INTO routes (
  slug, name, description, compatible_endpoints, sort_order, active
) VALUES
  (
    'cutaneous',
    '{"en-us": "Cutaneous", "pt-br": "Cutânea"}'::jsonb,
    '{"en-us": "Application to or exposure of the external skin surface; excludes injection into the dermis.", "pt-br": "Aplicação ou exposição à superfície externa da pele; exclui injeção na derme."}'::jsonb,
    ARRAY[3, 10, 11, 12, 17, 18, 20, 22, 23, 25, 26, 28, 29, 30]::int[],
    1, TRUE
  ),
  (
    'inhalation',
    '{"en-us": "Inhalation", "pt-br": "Inalação"}'::jsonb,
    '{"en-us": "Exposure through the respiratory tract to gases, vapours, aerosols or particles.", "pt-br": "Exposição pelo trato respiratório a gases, vapores, aerossóis ou partículas."}'::jsonb,
    ARRAY[17, 18, 22, 23, 25, 26, 28, 29, 30]::int[],
    2, TRUE
  ),
  (
    'oral',
    '{"en-us": "Oral", "pt-br": "Oral"}'::jsonb,
    '{"en-us": "Entry through the mouth and gastrointestinal tract, including administration by gavage, diet or drinking water.", "pt-br": "Entrada pela boca e pelo trato gastrointestinal, incluindo administração por gavagem, dieta ou água de beber."}'::jsonb,
    ARRAY[17, 18, 22, 23, 25, 26, 28, 29, 30]::int[],
    3, TRUE
  ),
  (
    'ocular',
    '{"en-us": "Ocular", "pt-br": "Ocular"}'::jsonb,
    '{"en-us": "Direct application to or exposure of the eye or ocular surface.", "pt-br": "Aplicação direta ou exposição do olho ou da superfície ocular."}'::jsonb,
    ARRAY[12, 14, 15]::int[],
    4, TRUE
  ),
  (
    'intranasal',
    '{"en-us": "Intranasal", "pt-br": "Intranasal"}'::jsonb,
    '{"en-us": "Administration into the nasal cavity.", "pt-br": "Administração na cavidade nasal."}'::jsonb,
    ARRAY[17, 18, 22, 23, 25, 26, 28, 29, 30]::int[],
    5, TRUE
  ),
  (
    'intratracheal',
    '{"en-us": "Intratracheal", "pt-br": "Intratraqueal"}'::jsonb,
    '{"en-us": "Administration directly into the trachea.", "pt-br": "Administração diretamente na traqueia."}'::jsonb,
    ARRAY[17, 18, 22, 23, 25, 26, 28, 29, 30]::int[],
    6, TRUE
  ),
  (
    'intravenous',
    '{"en-us": "Intravenous", "pt-br": "Intravenosa"}'::jsonb,
    '{"en-us": "Administration into a vein.", "pt-br": "Administração em uma veia."}'::jsonb,
    ARRAY[17, 18, 22, 23, 25, 26, 28, 29, 30, 48, 49, 50, 51]::int[],
    7, TRUE
  ),
  (
    'intra-arterial',
    '{"en-us": "Intra-arterial", "pt-br": "Intra-arterial"}'::jsonb,
    '{"en-us": "Administration into an artery.", "pt-br": "Administração em uma artéria."}'::jsonb,
    ARRAY[17, 18, 22, 23, 25, 26, 28, 29, 30]::int[],
    8, TRUE
  ),
  (
    'intramuscular',
    '{"en-us": "Intramuscular", "pt-br": "Intramuscular"}'::jsonb,
    '{"en-us": "Administration into muscle tissue.", "pt-br": "Administração no tecido muscular."}'::jsonb,
    ARRAY[17, 18, 22, 23, 25, 26, 28, 29, 30, 48, 49, 50, 51]::int[],
    9, TRUE
  ),
  (
    'subcutaneous',
    '{"en-us": "Subcutaneous", "pt-br": "Subcutânea"}'::jsonb,
    '{"en-us": "Administration into tissue beneath the skin.", "pt-br": "Administração no tecido localizado abaixo da pele."}'::jsonb,
    ARRAY[17, 18, 22, 23, 25, 26, 28, 29, 30, 48, 49, 50, 51]::int[],
    10, TRUE
  ),
  (
    'intradermal',
    '{"en-us": "Intradermal", "pt-br": "Intradérmica"}'::jsonb,
    '{"en-us": "Administration into the dermis.", "pt-br": "Administração na derme."}'::jsonb,
    ARRAY[17, 18, 20, 22, 23, 25, 26, 28, 29, 30]::int[],
    11, TRUE
  ),
  (
    'intraperitoneal',
    '{"en-us": "Intraperitoneal", "pt-br": "Intraperitoneal"}'::jsonb,
    '{"en-us": "Administration into the peritoneal cavity.", "pt-br": "Administração na cavidade peritoneal."}'::jsonb,
    ARRAY[17, 18, 22, 23, 25, 26, 28, 29, 30]::int[],
    12, TRUE
  ),
  (
    'rectal',
    '{"en-us": "Rectal", "pt-br": "Retal"}'::jsonb,
    '{"en-us": "Administration into or exposure through the rectum.", "pt-br": "Administração no reto ou exposição pela via retal."}'::jsonb,
    ARRAY[17, 18, 22, 23, 25, 26, 28, 29, 30]::int[],
    13, TRUE
  ),
  (
    'vaginal',
    '{"en-us": "Vaginal", "pt-br": "Vaginal"}'::jsonb,
    '{"en-us": "Administration into or exposure through the vagina.", "pt-br": "Administração na vagina ou exposição pela via vaginal."}'::jsonb,
    ARRAY[8, 17, 18, 20, 22, 23, 25, 26, 28, 29, 30]::int[],
    14, TRUE
  ),
  (
    'topical-mucosal',
    '{"en-us": "Topical mucosal", "pt-br": "Tópica em mucosa"}'::jsonb,
    '{"en-us": "Local application to a mucosal surface not represented by a more specific route.", "pt-br": "Aplicação local em uma superfície mucosa não representada por uma via mais específica."}'::jsonb,
    ARRAY[8, 17, 18, 20]::int[],
    15, TRUE
  ),
  (
    'implantation',
    '{"en-us": "Implantation", "pt-br": "Implantação"}'::jsonb,
    '{"en-us": "Placement of a test material or device within tissue or a body cavity.", "pt-br": "Colocação de um material de teste ou dispositivo em um tecido ou cavidade corporal."}'::jsonb,
    ARRAY[8, 17, 18, 20, 22, 23, 25, 26, 28, 29, 30]::int[],
    16, TRUE
  ),
  (
    'multiple',
    '{"en-us": "Multiple routes", "pt-br": "Múltiplas vias"}'::jsonb,
    '{"en-us": "Exposure or administration occurs through more than one route, but the individual routes are not recorded separately.", "pt-br": "A exposição ou administração ocorre por mais de uma via, mas as vias individuais não são registradas separadamente."}'::jsonb,
    ARRAY[]::int[],
    17, TRUE
  ),
  (
    'not-applicable',
    '{"en-us": "Not applicable", "pt-br": "Não aplicável"}'::jsonb,
    '{"en-us": "No organism-level exposure or administration route applies to the method or study.", "pt-br": "Nenhuma via de exposição ou administração em nível de organismo se aplica ao método ou estudo."}'::jsonb,
    ARRAY[]::int[],
    18, TRUE
  ),
  (
    'unspecified',
    '{"en-us": "Unspecified", "pt-br": "Não especificada"}'::jsonb,
    '{"en-us": "An exposure or administration route may exist, but it is not reported or cannot be determined.", "pt-br": "Pode existir uma via de exposição ou administração, mas ela não foi informada ou não pode ser determinada."}'::jsonb,
    ARRAY[]::int[],
    19, TRUE
  ),
  (
    'other',
    '{"en-us": "Other", "pt-br": "Outra"}'::jsonb,
    '{"en-us": "A known exposure or administration route not represented by the controlled vocabulary.", "pt-br": "Uma via conhecida de exposição ou administração não representada pelo vocabulário controlado."}'::jsonb,
    ARRAY[]::int[],
    20, TRUE
  );

INSERT INTO route_endpoints (route_code, endpoint_id)
SELECT r.slug, e.endpoint_id
FROM routes r
CROSS JOIN LATERAL unnest(COALESCE(r.compatible_endpoints, ARRAY[]::int[]))
  AS e(endpoint_id);

ALTER TABLE route_endpoints
  ADD CONSTRAINT route_endpoints_route_code_fkey
  FOREIGN KEY (route_code) REFERENCES routes(slug) ON DELETE CASCADE;

COMMIT;
