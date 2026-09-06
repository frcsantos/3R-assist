-- =============================================================================
-- Migration 061: applications vocabulary replaces methods.study_domain
-- =============================================================================

BEGIN;

CREATE TABLE applications (
    slug            TEXT            PRIMARY KEY,
    name            JSONB           NOT NULL,
    description     JSONB,
    sort_order      INTEGER         NOT NULL DEFAULT 0,
    active          BOOLEAN         NOT NULL DEFAULT TRUE,
    created_at      TIMESTAMPTZ     NOT NULL DEFAULT NOW(),
    updated_at      TIMESTAMPTZ     NOT NULL DEFAULT NOW()
);

CREATE INDEX idx_applications_active ON applications (active) WHERE active = TRUE;

CREATE TRIGGER applications_updated_at
    BEFORE UPDATE ON applications
    FOR EACH ROW EXECUTE FUNCTION set_updated_at();

INSERT INTO applications (slug, name, description, sort_order, active) VALUES
  (
    'basic-research',
    '{"en-us": "Basic research", "pt-br": "Pesquisa básica"}'::jsonb,
    '{"en-us": "Research conducted primarily to increase fundamental knowledge of biological, chemical or other phenomena, without an immediate practical or regulatory objective.", "pt-br": "Pesquisa realizada principalmente para ampliar o conhecimento fundamental sobre fenômenos biológicos, químicos ou outros, sem objetivo prático ou regulatório imediato."}'::jsonb,
    1, TRUE
  ),
  (
    'translational-applied-research',
    '{"en-us": "Translational and applied research", "pt-br": "Pesquisa translacional e aplicada"}'::jsonb,
    '{"en-us": "Research intended to apply or translate scientific knowledge toward a defined practical objective, including the prevention, diagnosis or treatment of disease and the improvement of human, animal or plant health and welfare.", "pt-br": "Pesquisa destinada a aplicar ou traduzir conhecimento científico para um objetivo prático definido, incluindo prevenção, diagnóstico ou tratamento de doenças e melhoria da saúde e do bem-estar humano, animal ou vegetal."}'::jsonb,
    2, TRUE
  ),
  (
    'regulatory-use',
    '{"en-us": "Regulatory use", "pt-br": "Uso regulatório"}'::jsonb,
    '{"en-us": "Use intended to generate information required, recommended or accepted by legislation or a regulatory authority for assessing the quality, safety, efficacy or environmental effects of a substance, product or intervention.", "pt-br": "Uso destinado a gerar informações exigidas, recomendadas ou aceitas pela legislação ou por uma autoridade regulatória para avaliar a qualidade, segurança, eficácia ou os efeitos ambientais de uma substância, produto ou intervenção."}'::jsonb,
    3, TRUE
  ),
  (
    'routine-production',
    '{"en-us": "Routine production", "pt-br": "Produção de rotina"}'::jsonb,
    '{"en-us": "Routine use associated with manufacturing, product consistency, quality control, potency testing or batch release, rather than research or initial method development.", "pt-br": "Uso rotineiro associado à fabricação, consistência do produto, controle de qualidade, ensaio de potência ou liberação de lotes, em vez de pesquisa ou desenvolvimento inicial de métodos."}'::jsonb,
    4, TRUE
  ),
  (
    'education-training',
    '{"en-us": "Education and training", "pt-br": "Ensino e treinamento"}'::jsonb,
    '{"en-us": "Use for teaching, demonstration or the acquisition, maintenance, improvement or assessment of academic, practical or professional knowledge and skills.", "pt-br": "Uso para ensino, demonstração ou aquisição, manutenção, aperfeiçoamento ou avaliação de conhecimentos e competências acadêmicas, práticas ou profissionais."}'::jsonb,
    5, TRUE
  ),
  (
    'environmental-protection',
    '{"en-us": "Protection of the natural environment", "pt-br": "Proteção do meio ambiente natural"}'::jsonb,
    '{"en-us": "Use primarily intended to protect the natural environment in the interests of the health or welfare of humans, animals or ecological systems.", "pt-br": "Uso destinado principalmente a proteger o meio ambiente natural em benefício da saúde ou do bem-estar de seres humanos, animais ou sistemas ecológicos."}'::jsonb,
    6, TRUE
  ),
  (
    'species-preservation',
    '{"en-us": "Preservation of species", "pt-br": "Preservação de espécies"}'::jsonb,
    '{"en-us": "Research or other use primarily intended to support the conservation, recovery or continued survival of a species or population.", "pt-br": "Pesquisa ou outro uso destinado principalmente a apoiar a conservação, recuperação ou sobrevivência continuada de uma espécie ou população."}'::jsonb,
    7, TRUE
  ),
  (
    'forensic-inquiry',
    '{"en-us": "Forensic inquiry", "pt-br": "Investigação forense"}'::jsonb,
    '{"en-us": "Use in an investigation conducted primarily for legal, judicial, criminalistic or other forensic purposes.", "pt-br": "Uso em investigação realizada principalmente para fins legais, judiciais, criminalísticos ou outros fins forenses."}'::jsonb,
    8, TRUE
  ),
  (
    'other',
    '{"en-us": "Other", "pt-br": "Outro"}'::jsonb,
    '{"en-us": "A known purpose that is not represented by another value in this controlled vocabulary.", "pt-br": "Uma finalidade conhecida que não é representada por outro valor deste vocabulário controlado."}'::jsonb,
    9, TRUE
  );

ALTER TABLE methods
  DROP CONSTRAINT IF EXISTS fk_methods_study_domain;

ALTER TABLE methods
  RENAME COLUMN study_domain TO application;

UPDATE methods
SET application = CASE application
  WHEN 'pharma' THEN 'regulatory-use'
  WHEN 'cosmetics' THEN 'regulatory-use'
  WHEN 'chemical_safety' THEN 'regulatory-use'
  ELSE 'basic-research'
END;

ALTER TABLE methods
  ADD CONSTRAINT fk_methods_application
  FOREIGN KEY (application) REFERENCES applications(slug);

COMMENT ON COLUMN methods.application IS
  'Intended use / purpose; FK → applications(slug).';
COMMENT ON COLUMN applications.name IS
  'Localized display name: {"en-us": "...", "pt-br": "..."}';
COMMENT ON COLUMN applications.description IS
  'Localized description: {"en-us": "...", "pt-br": "..."} (nullable)';

DROP TABLE IF EXISTS study_domains;

COMMIT;
