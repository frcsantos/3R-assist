-- =============================================================================
-- 3R Assist — Migration 003: Controlled vocabulary tables (PostgreSQL)
-- Tables: endpoints, routes, study_domains
-- Source: docs/parameter_model.md §3.1–3.3
-- Assumes: 001_initial.sql already applied (methods exist)
-- =============================================================================

-- ---------------------------------------------------------------------------
-- ENDPOINTS (parameter_model.md §3.1 endpoint_category)
-- ---------------------------------------------------------------------------

CREATE TABLE endpoints (
    code            TEXT            PRIMARY KEY,
    name_en         TEXT            NOT NULL,
    name_pt         TEXT            NOT NULL,
    description_en  TEXT,
    description_pt  TEXT,
    sort_order      INTEGER         NOT NULL DEFAULT 0,
    active          BOOLEAN         NOT NULL DEFAULT TRUE,
    created_at      TIMESTAMPTZ     NOT NULL DEFAULT NOW(),
    updated_at      TIMESTAMPTZ     NOT NULL DEFAULT NOW()
);

CREATE INDEX idx_endpoints_active ON endpoints (active) WHERE active = TRUE;

-- ---------------------------------------------------------------------------
-- ROUTES (parameter_model.md §3.2)
-- ---------------------------------------------------------------------------

CREATE TABLE routes (
    code            TEXT            PRIMARY KEY,
    name_en         TEXT            NOT NULL,
    name_pt         TEXT            NOT NULL,
    description_en  TEXT,
    description_pt  TEXT,
    sort_order      INTEGER         NOT NULL DEFAULT 0,
    active          BOOLEAN         NOT NULL DEFAULT TRUE,
    created_at      TIMESTAMPTZ     NOT NULL DEFAULT NOW(),
    updated_at      TIMESTAMPTZ     NOT NULL DEFAULT NOW()
);

CREATE INDEX idx_routes_active ON routes (active) WHERE active = TRUE;

-- ---------------------------------------------------------------------------
-- STUDY DOMAINS (parameter_model.md §3.3)
-- ---------------------------------------------------------------------------

CREATE TABLE study_domains (
    code            TEXT            PRIMARY KEY,
    name_en         TEXT            NOT NULL,
    name_pt         TEXT            NOT NULL,
    description_en  TEXT,
    description_pt  TEXT,
    sort_order      INTEGER         NOT NULL DEFAULT 0,
    active          BOOLEAN         NOT NULL DEFAULT TRUE,
    created_at      TIMESTAMPTZ     NOT NULL DEFAULT NOW(),
    updated_at      TIMESTAMPTZ     NOT NULL DEFAULT NOW()
);

CREATE INDEX idx_study_domains_active ON study_domains (active) WHERE active = TRUE;

-- ---------------------------------------------------------------------------
-- ROUTE ↔ ENDPOINT compatibility (parameter_model.md §3.2)
-- Used for route-based soft filtering in RetrievalService.
-- ---------------------------------------------------------------------------

CREATE TABLE route_endpoints (
    route_code      TEXT            NOT NULL REFERENCES routes(code) ON DELETE CASCADE,
    endpoint_code   TEXT            NOT NULL REFERENCES endpoints(code) ON DELETE CASCADE,
    PRIMARY KEY (route_code, endpoint_code)
);

CREATE INDEX idx_route_endpoints_endpoint ON route_endpoints (endpoint_code);

-- ---------------------------------------------------------------------------
-- TRIGGERS: keep updated_at current on vocabulary tables
-- ---------------------------------------------------------------------------

CREATE TRIGGER endpoints_updated_at
    BEFORE UPDATE ON endpoints
    FOR EACH ROW EXECUTE FUNCTION set_updated_at();

CREATE TRIGGER routes_updated_at
    BEFORE UPDATE ON routes
    FOR EACH ROW EXECUTE FUNCTION set_updated_at();

CREATE TRIGGER study_domains_updated_at
    BEFORE UPDATE ON study_domains
    FOR EACH ROW EXECUTE FUNCTION set_updated_at();

-- ---------------------------------------------------------------------------
-- SEED: endpoints
-- ---------------------------------------------------------------------------

INSERT INTO endpoints (code, name_en, name_pt, description_en, description_pt, sort_order) VALUES
(
    'acute_toxicity',
    'Acute toxicity',
    'Toxicidade aguda',
    'Acute oral, intraperitoneal, or intravenous toxicity; LD50, DL50, toxic class.',
    'Toxicidade aguda oral, intraperitoneal ou intravenosa; LD50, DL50, classe tóxica.',
    10
),
(
    'skin_irritation',
    'Skin irritation',
    'Irritação cutânea',
    'Skin irritation, dermal irritation, Draize skin test.',
    'Irritação cutânea, irritação dérmica, teste de Draize (pele).',
    20
),
(
    'skin_corrosion',
    'Skin corrosion',
    'Corrosão cutânea',
    'Skin corrosion, dermal corrosion.',
    'Corrosão cutânea, corrosão dérmica.',
    30
),
(
    'ocular_irritation',
    'Ocular irritation',
    'Irritação ocular',
    'Eye irritation, Draize eye test, conjunctival irritation.',
    'Irritação ocular, teste de Draize (olho), irritação conjuntival.',
    40
),
(
    'skin_sensitisation',
    'Skin sensitisation',
    'Sensibilização cutânea',
    'Skin sensitisation, allergenicity, LLNA.',
    'Sensibilização cutânea, alergenicidade, LLNA.',
    50
),
(
    'phototoxicity',
    'Phototoxicity',
    'Fototoxicidade',
    'Phototoxicity, photoirritation, 3T3 NRU.',
    'Fototoxicidade, fotoirritação, 3T3 NRU.',
    60
),
(
    'genotoxicity',
    'Genotoxicity',
    'Genotoxicidade',
    'Genotoxicity, mutagenicity, micronucleus, Ames test.',
    'Genotoxicidade, mutagenicidade, micronúcleo, teste de Ames.',
    70
),
(
    'pyrogenicity',
    'Pyrogenicity',
    'Pirogenicidade',
    'Pyrogenicity, endotoxin, monocyte activation test (MAT).',
    'Pirogenicidade, endotoxina, teste de ativação de monócitos (MAT).',
    80
),
(
    'skin_absorption',
    'Skin absorption',
    'Absorção cutânea',
    'Skin absorption, dermal penetration, percutaneous absorption.',
    'Absorção cutânea, penetração dérmica, absorção percutânea.',
    90
);

-- ---------------------------------------------------------------------------
-- SEED: routes
-- ---------------------------------------------------------------------------

INSERT INTO routes (code, name_en, name_pt, description_en, description_pt, sort_order) VALUES
(
    'oral',
    'Oral',
    'Oral',
    'p.o., gavage, intragastric, gastric tube, dietary administration.',
    'p.o., gavagem, intragástrico, sonda gástrica, administração via dieta.',
    10
),
(
    'intraperitoneal',
    'Intraperitoneal',
    'Intraperitoneal',
    'i.p. administration.',
    'Administração i.p.',
    20
),
(
    'intravenous',
    'Intravenous',
    'Intravenosa',
    'i.v., intravenous administration.',
    'i.v., administração endovenosa.',
    30
),
(
    'dermal',
    'Dermal',
    'Dérmica',
    'Topical, cutaneous, ex vivo skin disc, membrane model.',
    'Tópico, cutâneo, disco de pele ex vivo, modelo de membrana.',
    40
),
(
    'ocular',
    'Ocular',
    'Ocular',
    'Conjunctival, corneal application, ex vivo corneal application.',
    'Conjuntival, aplicação corneana, aplicação corneana ex vivo.',
    50
),
(
    'inhalation',
    'Inhalation',
    'Inalação',
    'Inhalation, respiratory, aerosol, nose-only chamber.',
    'Inalação, respiratório, aerossol, câmara nose-only.',
    60
),
(
    'in_vitro',
    'In vitro',
    'In vitro',
    'Cell suspension, well plate, monolayer culture.',
    'Célula em suspensão, placa de poços, cultura em monocamada.',
    70
),
(
    'other',
    'Other',
    'Outra',
    'Any chemical administration route not covered by the controlled list.',
    'Qualquer via de administração química não coberta pela lista controlada.',
    80
);

-- ---------------------------------------------------------------------------
-- SEED: study_domains
-- ---------------------------------------------------------------------------

INSERT INTO study_domains (code, name_en, name_pt, description_en, description_pt, sort_order) VALUES
(
    'pharma',
    'Pharmaceutical',
    'Farmacêutico',
    'Pharmaceutical safety, regulatory drug and vaccine testing.',
    'Segurança farmacêutica, testes regulatórios de medicamentos e vacinas.',
    10
),
(
    'cosmetics',
    'Cosmetics',
    'Cosméticos',
    'Cosmetics and personal care products.',
    'Cosméticos e produtos de higiene pessoal.',
    20
),
(
    'chemical_safety',
    'Chemical safety',
    'Segurança química',
    'Industrial chemicals, pesticides, food additive safety.',
    'Substâncias químicas industriais, agrotóxicos, segurança de aditivos alimentares.',
    30
),
(
    'general',
    'General',
    'Geral',
    'Basic research without a specific regulatory context; fallback when undetermined.',
    'Pesquisa básica sem contexto regulatório específico; fallback quando indeterminado.',
    40
);

-- ---------------------------------------------------------------------------
-- SEED: route ↔ endpoint compatibility (parameter_model.md §3.2)
-- ---------------------------------------------------------------------------

INSERT INTO route_endpoints (route_code, endpoint_code) VALUES
    ('oral', 'acute_toxicity'),
    ('intraperitoneal', 'acute_toxicity'),
    ('intravenous', 'acute_toxicity'),
    ('dermal', 'skin_irritation'),
    ('dermal', 'skin_corrosion'),
    ('dermal', 'skin_sensitisation'),
    ('dermal', 'skin_absorption'),
    ('dermal', 'phototoxicity'),
    ('ocular', 'ocular_irritation'),
    ('in_vitro', 'genotoxicity'),
    ('in_vitro', 'phototoxicity');

-- ---------------------------------------------------------------------------
-- FK constraints on methods (replaces inline CHECK on study_domain)
-- ---------------------------------------------------------------------------

ALTER TABLE methods
    ADD CONSTRAINT fk_methods_endpoint_category
        FOREIGN KEY (endpoint_category) REFERENCES endpoints(code);

ALTER TABLE methods
    DROP CONSTRAINT IF EXISTS methods_study_domain_check;

ALTER TABLE methods
    ADD CONSTRAINT fk_methods_study_domain
        FOREIGN KEY (study_domain) REFERENCES study_domains(code);

-- ---------------------------------------------------------------------------
-- VERIFICATION QUERIES
-- ---------------------------------------------------------------------------
-- SELECT COUNT(*) FROM endpoints;           -- expect 9
-- SELECT COUNT(*) FROM routes;            -- expect 8
-- SELECT COUNT(*) FROM study_domains;       -- expect 4
-- SELECT COUNT(*) FROM route_endpoints;     -- expect 11
-- SELECT code, name_en FROM endpoints ORDER BY sort_order;
-- SELECT code, name_en FROM routes ORDER BY sort_order;
-- SELECT code, name_en FROM study_domains ORDER BY sort_order;
