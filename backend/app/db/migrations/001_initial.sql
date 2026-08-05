-- db/migrations/001_initial.sql
-- 3R Assist — methods + method_keywords + method_validation_contexts
-- ADR-013: PostgreSQL
-- ADR-020: study_domain (renamed from application_area)
-- ADR-021: category_3r JSONB (multiple 3R values per method)
-- ADR-022: method_validation_contexts; jurisdiction vocabulary brazil|eu|us|oecd
--
-- ncit_id: NCI Thesaurus concept ID — map per endpoint_category at
--   https://ncit.nci.nih.gov/ and UPDATE methods SET ncit_id = '...'
--   WHERE endpoint_category = '...'; all NULL until Karynn maps them.
--
-- source_db values:
--   OECD_TG        — curated directly from OECD Test Guideline document
--   ECVAM_DBALM    — curated from ECVAM DB-ALM entry
--   NICEATM        — curated from NICEATM / ICCVAM publication
--   FARMACOPEIA_BR — curated from Farmacopeia Brasileira chapter
--   TSAR           — curated from ECVAM TSAR database
--
-- jurisdiction values (method_validation_contexts.jurisdiction):
--   brazil — CONCEA / ANVISA / MAPA recognition
--   eu     — ECHA (REACH), EMA, EU Cosmetics Regulation 1223/2009, EFSA
--   us     — FDA, EPA, ICCVAM / NICEATM
--   oecd   — adopted as OECD Test Guideline; 38-member acceptance subject to national adoption
--
-- All methods: active = FALSE pending Karynn review (karynn_review_checklist.md)

-- ── Shared trigger function ─────────────────────────────────────────────────

CREATE OR REPLACE FUNCTION set_updated_at()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- ── Tables ─────────────────────────────────────────────────────────────────

CREATE TABLE IF NOT EXISTS methods (
    id                  SERIAL      PRIMARY KEY,
    slug                TEXT        NOT NULL UNIQUE,
    name_en             TEXT        NOT NULL,
    name_pt             TEXT        NOT NULL,
    description_en      TEXT        NOT NULL,
    description_pt      TEXT        NOT NULL,
    text_for_embedding  TEXT        NOT NULL,   -- English only; exact string used at embed time
    category_3r         JSONB       NOT NULL,   -- e.g. '["replacement"]' '["reduction","refinement"]'
    endpoint_category   TEXT        NOT NULL,   -- see parameter_model.md §3.1
    study_domain        TEXT        NOT NULL,   -- 'general'|'pharma'|'cosmetics'|'chemical_safety'
    oecd_tg_ref         TEXT,                   -- e.g. 'TG 439', 'GD 129'; NULL for non-OECD methods
    ncit_id             TEXT,                   -- NCI Thesaurus concept ID [VERIFY]
    source_db           TEXT        NOT NULL,   -- see header
    routes_applicable   JSONB,                  -- e.g. '["dermal"]'; NULL = route-agnostic
    embedding_json      JSONB,                  -- 384-dim float array; NULL until embed_methods.py runs
    active              BOOLEAN     NOT NULL DEFAULT FALSE,
    created_at          TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at          TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- Validation status and jurisdiction are per method × study_domain × jurisdiction.
-- Do NOT add validation_status or jurisdiction columns to methods.
CREATE TABLE IF NOT EXISTS method_validation_contexts (
    id                SERIAL      PRIMARY KEY,
    method_id         INTEGER     NOT NULL REFERENCES methods(id) ON DELETE CASCADE,
    study_domain      TEXT        NOT NULL,   -- 'general'|'pharma'|'cosmetics'|'chemical_safety'
    jurisdiction      TEXT        NOT NULL,   -- 'brazil'|'eu'|'us'|'oecd'
    validation_status TEXT        NOT NULL,   -- 'validated'|'accepted'|'emerging'
    purpose           TEXT,                   -- what the method is recognized/validated for in this context
    regulatory_status TEXT,                   -- 'not_approved'|'approved'|'recommended'|'mandatory'
    regulatory_body   TEXT,                   -- 'CONCEA'|'ANVISA'|'ECHA'|'EMA'|'EPA'|'FDA'|'ICCVAM'|'OECD'
    regulatory_ref    TEXT,                   -- e.g. 'RN 18/2014 Art. 2', 'TG 439', 'Reg 1223/2009'
    regulatory_url    TEXT,
    notes             TEXT,
    created_at        TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    UNIQUE (method_id, study_domain, jurisdiction),
    CONSTRAINT method_validation_contexts_regulatory_status_check CHECK (
        regulatory_status IS NULL
        OR regulatory_status IN (
            'not_approved',
            'approved',
            'recommended',
            'mandatory'
        )
    )
);

CREATE TABLE IF NOT EXISTS method_keywords (
    id          SERIAL  PRIMARY KEY,
    method_id   INTEGER NOT NULL REFERENCES methods(id) ON DELETE CASCADE,
    keyword     TEXT    NOT NULL,
    language    TEXT    NOT NULL    -- 'en' | 'pt'
);

CREATE INDEX IF NOT EXISTS idx_methods_endpoint       ON methods(endpoint_category);
CREATE INDEX IF NOT EXISTS idx_methods_active         ON methods(active);
CREATE INDEX IF NOT EXISTS idx_methods_category_3r    ON methods USING gin(category_3r);
CREATE INDEX IF NOT EXISTS idx_mvc_method             ON method_validation_contexts(method_id);
CREATE INDEX IF NOT EXISTS idx_mvc_jurisdiction       ON method_validation_contexts(jurisdiction);
CREATE INDEX IF NOT EXISTS idx_mvc_domain_juris       ON method_validation_contexts(study_domain, jurisdiction);
CREATE INDEX IF NOT EXISTS idx_keywords_method        ON method_keywords(method_id);

-- ── Methods seed ────────────────────────────────────────────────────────────
-- category_3r marked [VERIFY] where classification is ambiguous (see ADR-021).
-- Karynn resolves via karynn_review_checklist.md before active = TRUE.

INSERT INTO methods (
    slug, name_en, name_pt,
    description_en, description_pt, text_for_embedding,
    category_3r, endpoint_category, study_domain,
    oecd_tg_ref, ncit_id, source_db,
    routes_applicable, active
) VALUES

-- ── Skin irritation ─────────────────────────────────────────────────────────

('oecd-tg439-epiderm',
 'EpiDerm™ Skin Irritation Test (OECD TG 439)',
 'Teste de Irritação Cutânea EpiDerm™ (OECD TG 439)',
 'In vitro skin irritation test using the EpiDerm™ reconstructed human epidermis (RHE) model. '
 'Topical application for 60 minutes; cell viability by MTT assay. '
 'Predicts UN GHS Category 2 skin irritants and non-irritants.',
 'Teste de irritação cutânea in vitro com modelo de epiderme humana reconstituída EpiDerm™. '
 'Aplicação tópica por 60 minutos; viabilidade celular por MTT. '
 'Prediz irritantes cutâneos GHS Categoria 2 e não irritantes.',
 'skin_irritation reconstructed human epidermis RHE MTT viability topical dermal in vitro replacement general',
 '["replacement"]', 'skin_irritation', 'general',
 'TG 439', NULL, 'OECD_TG', '["dermal"]', FALSE),

('oecd-tg439-episkin',
 'EpiSkin™ Skin Irritation Test (OECD TG 439)',
 'Teste de Irritação Cutânea EpiSkin™ (OECD TG 439)',
 'In vitro skin irritation test using the EpiSkin™ reconstructed human epidermis model. '
 'Topical application for 15 minutes; cell viability by MTT assay. '
 'ECVAM-validated; OECD TG 439 compliant.',
 'Teste de irritação cutânea in vitro com modelo de epiderme humana reconstituída EpiSkin™. '
 'Aplicação tópica por 15 minutos; viabilidade celular por MTT. '
 'Validado pela ECVAM; conforme OECD TG 439.',
 'skin_irritation reconstructed human epidermis RHE EpiSkin MTT viability topical dermal in vitro replacement general',
 '["replacement"]', 'skin_irritation', 'general',
 'TG 439', NULL, 'OECD_TG', '["dermal"]', FALSE),

-- ── Skin corrosion ──────────────────────────────────────────────────────────

('oecd-tg431-rhe-corrosion',
 'Reconstructed Human Epidermis Skin Corrosion Test (OECD TG 431)',
 'Teste de Corrosão Cutânea em Epiderme Humana Reconstituída (OECD TG 431)',
 'In vitro skin corrosion test using reconstructed human epidermis models (EpiDerm™, EpiSkin™). '
 'Test substance applied for 3 and 60 minutes; cell viability by MTT. '
 'Distinguishes corrosive categories (GHS 1A, 1B, 1C) from non-corrosives.',
 'Teste de corrosão cutânea in vitro com epiderme humana reconstituída. '
 'Aplicação por 3 e 60 minutos; viabilidade por MTT. '
 'Distingue categorias corrosivas GHS 1A, 1B, 1C de não corrosivos.',
 'skin_corrosion reconstructed human epidermis RHE MTT viability dermal in vitro replacement general',
 '["replacement"]', 'skin_corrosion', 'general',
 'TG 431', NULL, 'OECD_TG', '["dermal"]', FALSE),

('oecd-tg430-ter-corrosion',
 'Transcutaneous Electrical Resistance (TER) Skin Corrosion Test (OECD TG 430)',
 'Teste de Corrosão Cutânea por Resistência Elétrica Transcutânea (OECD TG 430)',
 'Ex vivo skin corrosion test using rat skin discs in diffusion chambers. '
 'Measures TER as indicator of membrane integrity disruption. '
 'Identifies corrosive substances (UN GHS Category 1).',
 'Teste de corrosão cutânea ex vivo com discos de pele de rato em câmaras de difusão. '
 'Mede resistência elétrica transcutânea como indicador de ruptura da integridade da membrana.',
 'skin_corrosion transcutaneous electrical resistance TER rat skin ex vivo membrane dermal replacement general',
 '["replacement"]', 'skin_corrosion', 'general',
 'TG 430', NULL, 'OECD_TG', '["dermal"]', FALSE),

('oecd-tg435-membrane-barrier',
 'Membrane Barrier Test (CORROSITEX®) for Skin Corrosion (OECD TG 435)',
 'Teste de Barreira de Membrana (CORROSITEX®) para Corrosão Cutânea (OECD TG 435)',
 'In vitro skin corrosion test using a synthetic macromolecular biobarrier membrane (CORROSITEX®). '
 'Time to color change in detection system indicates corrosion potential. '
 'Applicable to substances with pH < 2 or > 11.5.',
 'Teste de corrosão cutânea in vitro com membrana biobarreira sintética CORROSITEX®. '
 'Tempo para mudança de cor indica potencial de corrosão. '
 'Aplicável a substâncias com pH < 2 ou > 11,5.',
 'skin_corrosion synthetic membrane biobarrier CORROSITEX pH acidic alkaline dermal in vitro replacement general',
 '["replacement"]', 'skin_corrosion', 'general',
 'TG 435', NULL, 'OECD_TG', '["dermal"]', FALSE),

-- ── Ocular irritation ───────────────────────────────────────────────────────

('oecd-tg437-bcop',
 'Bovine Corneal Opacity and Permeability (BCOP) Assay (OECD TG 437)',
 'Ensaio de Opacidade e Permeabilidade da Córnea Bovina (BCOP) (OECD TG 437)',
 'Ex vivo ocular irritation test using freshly isolated bovine corneas from slaughterhouse. '
 'Measures corneal opacity and fluorescein permeability after topical substance application. '
 'Identifies ocular corrosives and severe irritants (GHS Category 1).',
 'Teste de irritação ocular ex vivo com córneas bovinas frescas de abatedouro. '
 'Mede opacidade corneana e permeabilidade à fluoresceína após aplicação tópica. '
 'Identifica corrosivos oculares e irritantes graves (GHS Categoria 1).',
 'ocular_irritation bovine cornea opacity permeability fluorescein BCOP ex vivo slaughterhouse topical ocular replacement general',
 '["replacement"]', 'ocular_irritation', 'general',
 'TG 437', NULL, 'OECD_TG', '["ocular"]', FALSE),

('oecd-tg438-ice',
 'Isolated Chicken Eye (ICE) Test (OECD TG 438)',
 'Teste do Olho de Galinha Isolado (ICE) (OECD TG 438)',
 'Ex vivo ocular irritation test using eyes from slaughterhouse chickens. '
 'Measures corneal opacity, iris lesions, and fluorescein retention. '
 'Applicable to water-soluble substances and surfactants.',
 'Teste de irritação ocular ex vivo com olhos de galinhas de abatedouro. '
 'Mede opacidade corneana, lesões de íris e retenção de fluoresceína. '
 'Aplicável a substâncias solúveis em água e surfactantes.',
 'ocular_irritation isolated chicken eye ICE corneal opacity iris fluorescein ex vivo poultry ocular replacement general',
 '["replacement"]', 'ocular_irritation', 'general',
 'TG 438', NULL, 'OECD_TG', '["ocular"]', FALSE),

('oecd-tg492-rce',
 'Reconstructed Human Cornea-like Epithelium (RCE) Test (OECD TG 492)',
 'Teste de Epitélio Semelhante à Córnea Humana Reconstituída (RCE) (OECD TG 492)',
 'In vitro ocular irritation test using reconstructed human cornea-like epithelium models. '
 'Topical application; cell viability by MTT. '
 'Identifies non-irritants and mild irritants (GHS Category 2 and non-classified).',
 'Teste de irritação ocular in vitro com epitélio semelhante à córnea humana reconstituída. '
 'Aplicação tópica; viabilidade celular por MTT. '
 'Identifica não irritantes e irritantes leves (GHS Categoria 2 e não classificados).',
 'ocular_irritation reconstructed human cornea epithelium RCE MTT viability topical in vitro replacement general',
 '["replacement"]', 'ocular_irritation', 'general',
 'TG 492', NULL, 'OECD_TG', '["ocular"]', FALSE),

('oecd-tg460-fluorescein-leakage',
 'Fluorescein Leakage (FL) Test (OECD TG 460)',
 'Teste de Extravasamento de Fluoresceína (FL) (OECD TG 460)',
 'In vitro ocular irritation test measuring disruption of tight junctions in MDCK cell monolayers '
 'using fluorescein transport as surrogate for corneal barrier integrity. '
 'Identifies non-irritants and mild irritants; complementary method in testing strategy.',
 'Teste de irritação ocular in vitro que mede disrupção de junções compactas em monocamadas MDCK '
 'usando transporte de fluoresceína como indicador da integridade da barreira corneana.',
 'ocular_irritation fluorescein leakage MDCK tight junctions corneal barrier in vitro cell monolayer replacement general',
 '["replacement"]', 'ocular_irritation', 'general',
 'TG 460', NULL, 'OECD_TG', '["ocular"]', FALSE),

-- ── Skin sensitisation ──────────────────────────────────────────────────────

('oecd-tg442c-dpra',
 'Direct Peptide Reactivity Assay (DPRA) (OECD TG 442C)',
 'Ensaio de Reatividade Direta com Peptídeos (DPRA) (OECD TG 442C)',
 'In chemico skin sensitisation assay measuring covalent binding of test substance '
 'to synthetic cysteine and lysine peptides by HPLC. '
 'Addresses AOP key event 1 (haptenation). Used in defined approaches for non-animal assessment.',
 'Ensaio in chemico para sensibilização cutânea que mede ligação covalente da substância '
 'a peptídeos de cisteína e lisina por HPLC. '
 'Aborda evento-chave 1 do AOP (haptenação). Usado em abordagens definidas sem animais.',
 'skin_sensitisation peptide reactivity DPRA haptenation cysteine lysine HPLC in chemico AOP key event 1 replacement general',
 '["replacement"]', 'skin_sensitisation', 'general',
 'TG 442C', NULL, 'OECD_TG', '["dermal"]', FALSE),

('oecd-tg442d-keratinosens',
 'KeratinoSens™ ARE-Nrf2 Luciferase Assay (OECD TG 442D)',
 'Ensaio de Luciferase ARE-Nrf2 KeratinoSens™ (OECD TG 442D)',
 'In vitro skin sensitisation assay using HaCaT keratinocytes with ARE-driven luciferase reporter. '
 'Quantifies Nrf2-dependent gene induction (AOP key event 2). '
 'Included in OECD defined approaches for skin sensitisation.',
 'Ensaio in vitro para sensibilização cutânea com queratinócitos HaCaT e repórter ARE-luciferase. '
 'Quantifica indução gênica Nrf2-dependente (evento-chave 2 do AOP).',
 'skin_sensitisation keratinocyte Nrf2 ARE luciferase HaCaT gene induction in vitro KE2 AOP replacement general',
 '["replacement"]', 'skin_sensitisation', 'general',
 'TG 442D', NULL, 'OECD_TG', '["dermal"]', FALSE),

('oecd-tg442e-hclat',
 'Human Cell Line Activation Test (h-CLAT) (OECD TG 442E)',
 'Teste de Ativação de Linhagem Celular Humana (h-CLAT) (OECD TG 442E)',
 'In vitro skin sensitisation assay using THP-1 monocytic cells. '
 'Measures CD54 and CD86 upregulation by flow cytometry as surrogate for '
 'dendritic cell activation (AOP key event 3).',
 'Ensaio in vitro para sensibilização cutânea com células monocíticas THP-1. '
 'Mede regulação positiva de CD54 e CD86 por citometria de fluxo '
 'como indicador da ativação de células dendríticas (evento-chave 3 do AOP).',
 'skin_sensitisation THP-1 monocyte CD54 CD86 flow cytometry dendritic cell activation KE3 AOP in vitro replacement general',
 '["replacement"]', 'skin_sensitisation', 'general',
 'TG 442E', NULL, 'OECD_TG', '["dermal"]', FALSE),

('oecd-tg429-llna',
 'Local Lymph Node Assay (LLNA) (OECD TG 429)',
 'Ensaio do Linfonodo Local (LLNA) (OECD TG 429)',
 'In vivo murine skin sensitisation assay. '
 'Test substance applied to ear pinnae of CBA/J mice for 3 days; '
 'auricular lymph node proliferation measured by 3H-thymidine incorporation. '
 'Replaces guinea pig Buehler and GPMT tests; provides quantitative EC3 endpoint.',
 'Ensaio murino de sensibilização cutânea in vivo. '
 'Substância aplicada nas orelhas de camundongos CBA/J por 3 dias; '
 'proliferação do linfonodo auricular medida por incorporação de 3H-timidina. '
 'Substitui os testes de Buehler e GPMT em cobaia.',
 'skin_sensitisation local lymph node LLNA mouse CBA thymidine proliferation ear pinna in vivo replacement general',
 '["replacement"]', 'skin_sensitisation', 'general',  -- [VERIFY: replacement vs reduction/refinement — see ADR-021]
 'TG 429', NULL, 'OECD_TG', '["dermal"]', FALSE),

('oecd-tg442a-llna-da',
 'LLNA: DA — Non-Radioactive Local Lymph Node Assay (OECD TG 442A)',
 'LLNA: DA — Ensaio do Linfonodo Local Não Radioativo (OECD TG 442A)',
 'Non-radioactive variant of the LLNA for skin sensitisation. '
 'Replaces 3H-thymidine with ATP content measurement (DA). '
 'Eliminates radioactive waste handling while retaining LLNA protocol.',
 'Variante não radioativa do LLNA para sensibilização cutânea. '
 'Substitui 3H-timidina pela medição de ATP. '
 'Elimina manejo de resíduos radioativos mantendo o protocolo LLNA.',
 'skin_sensitisation local lymph node LLNA DA ATP non-radioactive mouse ear pinna in vivo refinement general',
 '["refinement"]', 'skin_sensitisation', 'general',  -- [VERIFY: refinement of TG429; also replacement of GPMT?]
 'TG 442A', NULL, 'OECD_TG', '["dermal"]', FALSE),

('oecd-tg442b-llna-brdu',
 'LLNA: BrdU-ELISA — Non-Radioactive Local Lymph Node Assay (OECD TG 442B)',
 'LLNA: BrdU-ELISA — Ensaio do Linfonodo Local Não Radioativo (OECD TG 442B)',
 'Non-radioactive LLNA variant using BrdU incorporation measured by ELISA '
 'as marker of lymphocyte proliferation. '
 'Quantitative sensitisation potency without radioactive materials.',
 'Variante não radioativa do LLNA com incorporação de BrdU medida por ELISA '
 'como marcador de proliferação linfocitária. '
 'Avaliação quantitativa do potencial de sensibilização sem radioatividade.',
 'skin_sensitisation local lymph node LLNA BrdU ELISA non-radioactive mouse in vivo refinement general',
 '["refinement"]', 'skin_sensitisation', 'general',  -- [VERIFY: same as TG 442A]
 'TG 442B', NULL, 'OECD_TG', '["dermal"]', FALSE),

-- ── Phototoxicity ───────────────────────────────────────────────────────────

('oecd-tg432-3t3nru',
 '3T3 NRU Phototoxicity Test (OECD TG 432)',
 'Teste de Fototoxicidade 3T3 NRU (OECD TG 432)',
 'In vitro phototoxicity test using Balb/c 3T3 mouse fibroblasts. '
 'Compares cytotoxicity (neutral red uptake) with and without UV-A irradiation. '
 'Photo-irritation factor (PIF) and mean photo effect (MPE) predict phototoxic potential.',
 'Teste de fototoxicidade in vitro com fibroblastos murinos Balb/c 3T3. '
 'Compara citotoxicidade (captação de vermelho neutro) com e sem irradiação UV-A. '
 'Fator de foto-irritação (PIF) e efeito foto médio (MPE) predizem potencial fototóxico.',
 'phototoxicity 3T3 fibroblast NRU neutral red uptake UV-A irradiation photo-irritation PIF MPE in vitro replacement general',
 '["replacement"]', 'phototoxicity', 'general',
 'TG 432', NULL, 'OECD_TG', '["dermal"]', FALSE),

-- ── Skin absorption ─────────────────────────────────────────────────────────

('oecd-tg428-skin-absorption-vitro',
 'In Vitro Skin Absorption Test (Franz Diffusion Cell) (OECD TG 428)',
 'Teste de Absorção Cutânea In Vitro (Célula de Difusão de Franz) (OECD TG 428)',
 'In vitro percutaneous absorption test using Franz diffusion cells with excised skin '
 '(human cadaver, pig ear, or rat skin). '
 'Measures penetration of test substance through skin membrane over time.',
 'Teste de absorção percutânea in vitro com células de difusão de Franz e pele excisada '
 '(cadáver humano, orelha de porco ou pele de rato). '
 'Mede penetração da substância através da membrana cutânea ao longo do tempo.',
 'skin_absorption percutaneous absorption Franz diffusion cell excised skin human pig rat penetration dermal in vitro replacement general',
 '["replacement"]', 'skin_absorption', 'general',
 'TG 428', NULL, 'OECD_TG', '["dermal"]', FALSE),

-- ── Genotoxicity ────────────────────────────────────────────────────────────

('oecd-tg471-ames',
 'Bacterial Reverse Mutation Test (Ames Test) (OECD TG 471)',
 'Teste de Mutação Reversa em Bactérias (Teste de Ames) (OECD TG 471)',
 'In vitro bacterial mutagenicity assay using Salmonella typhimurium '
 'and E. coli auxotrophic strains. '
 'Detects point mutations with and without metabolic activation (S9 fraction).',
 'Ensaio de mutagenicidade bacteriana in vitro com cepas auxotróficas de '
 'Salmonella typhimurium e E. coli. '
 'Detecta mutações pontuais com e sem ativação metabólica (fração S9).',
 'genotoxicity mutagenicity bacterial reverse mutation Ames Salmonella histidine frameshift S9 metabolic activation in vitro replacement general',
 '["replacement"]', 'genotoxicity', 'general',
 'TG 471', NULL, 'OECD_TG', NULL, FALSE),

('oecd-tg476-hprt',
 'In Vitro Mammalian Cell Gene Mutation Test (HPRT/XPRT) (OECD TG 476)',
 'Teste de Mutação Gênica em Células de Mamíferos In Vitro (HPRT/XPRT) (OECD TG 476)',
 'In vitro gene mutation test using mammalian cells (CHO, V79, L5178Y, TK6). '
 'Detects forward mutations at the HPRT locus conferring 6-thioguanine resistance. '
 'Detects point mutations, small deletions, and frameshifts.',
 'Teste de mutação gênica in vitro com células de mamíferos (CHO, V79, L5178Y, TK6). '
 'Detecta mutações diretas no locus HPRT conferindo resistência a 6-tioguanina.',
 'genotoxicity gene mutation HPRT XPRT CHO V79 6-thioguanine forward mutation mammalian cell in vitro replacement general',
 '["replacement"]', 'genotoxicity', 'general',
 'TG 476', NULL, 'OECD_TG', NULL, FALSE),

('oecd-tg487-micronucleus',
 'In Vitro Mammalian Cell Micronucleus Test (MNvit) (OECD TG 487)',
 'Teste de Micronúcleo em Células de Mamíferos In Vitro (MNvit) (OECD TG 487)',
 'In vitro genotoxicity test detecting micronuclei in interphase cells. '
 'Identifies clastogenicity (chromosome fragments) and aneugenicity (whole chromosomes). '
 'Uses human lymphocytes, CHO, V79, or other mammalian cell lines.',
 'Teste de genotoxicidade in vitro que detecta micronúcleos em células em interfase. '
 'Identifica clastogenicidade e aneugeneticidade. '
 'Utiliza linfócitos humanos, CHO, V79 ou outras linhagens de mamíferos.',
 'genotoxicity micronucleus clastogenicity aneugenicity chromosome fragment in vitro human lymphocyte CHO S9 replacement general',
 '["replacement"]', 'genotoxicity', 'general',
 'TG 487', NULL, 'OECD_TG', NULL, FALSE),

-- ── Pyrogenicity ────────────────────────────────────────────────────────────

('mat-monocyte-activation',
 'Monocyte Activation Test (MAT) for Pyrogenicity',
 'Teste de Ativação de Monócitos (MAT) para Pirogenicidade',
 'In vitro pyrogenicity test using human PBMCs or MonoMac 6 cell line. '
 'Detects pyrogenic contaminants (endotoxins and non-endotoxin pyrogens) '
 'by measuring pro-inflammatory cytokine release (IL-1β, IL-6, TNF-α). '
 'Replaces the rabbit pyrogen test (RPT).',
 'Teste de pirogenicidade in vitro com PBMCs humanos ou linhagem MonoMac 6. '
 'Detecta contaminantes pirogênicos por medição de citocinas pró-inflamatórias (IL-1β, IL-6, TNF-α). '
 'Substitui o teste de pirogênio em coelhos.',
 'pyrogenicity pyrogen endotoxin monocyte activation MAT PBMC IL-6 TNF cytokine in vitro human blood replacement general',
 '["replacement"]', 'pyrogenicity', 'general',
 NULL, NULL, 'FARMACOPEIA_BR',  -- source_db [VERIFY]; oecd_tg_ref NULL (no standalone OECD TG)
 NULL, FALSE),

-- ── Acute toxicity — replacement ────────────────────────────────────────────

('niceatm-cytotox-basal-barranco',
 'Basal Cytotoxicity Assay for Acute Oral Toxicity Starting Dose (Barranco et al.)',
 'Ensaio de Citotoxicidade Basal para Dose Inicial de Toxicidade Aguda Oral (Barranco et al.)',
 'In vitro cytotoxicity assay using multiple cell lines to estimate LD50 starting doses '
 'for in vivo acute oral toxicity studies. '
 'Based on the principle that acute lethality correlates with basal cytotoxicity. '
 'Developed by NICEATM/ICCVAM; reduces animals by refining dose selection.',
 'Ensaio de citotoxicidade in vitro com múltiplas linhagens celulares para estimar doses iniciais de DL50 '
 'para estudos de toxicidade aguda oral in vivo. '
 'Baseado na correlação entre letalidade aguda e citotoxicidade basal. '
 'Desenvolvido pelo NICEATM/ICCVAM.',
 'acute_toxicity LD50 basal cytotoxicity in vitro dose estimation starting dose oral NICEATM ICCVAM replacement general',
 '["replacement","reduction"]', 'acute_toxicity', 'general',
 'GD 129', NULL, 'NICEATM',
 '["oral"]', FALSE),

-- ── Acute toxicity — in vivo refinement ─────────────────────────────────────
-- Still in vivo; reduce animal use and remove lethality as required endpoint.
-- Included because RN 18/2014 recognizes them and CEUAs evaluate humaneness
-- relative to classical LD50 (Litchfield-Wilcoxon). See ADR-021.

('oecd-tg420-fixed-dose',
 'Fixed Dose Procedure for Acute Oral Toxicity (OECD TG 420)',
 'Procedimento de Dose Fixa para Toxicidade Aguda Oral (OECD TG 420)',
 'In vivo acute oral toxicity test using fixed dose levels (5, 50, 300, 2000 mg/kg). '
 'Stepwise dosing; endpoint is evident toxicity, not lethality. '
 'Uses significantly fewer animals than classical LD50.',
 'Teste de toxicidade aguda oral in vivo com doses fixas (5, 50, 300, 2000 mg/kg). '
 'Endpoint é toxicidade evidente, não letalidade. '
 'Usa significativamente menos animais que a DL50 clássica.',
 'acute_toxicity fixed dose procedure oral GHS classification stepwise in vivo rat reduction refinement general',
 '["reduction","refinement"]', 'acute_toxicity', 'general',
 'TG 420', NULL, 'OECD_TG', '["oral"]', FALSE),

('oecd-tg423-atc',
 'Acute Toxic Class (ATC) Method for Acute Oral Toxicity (OECD TG 423)',
 'Método de Classe Tóxica Aguda (ATC) para Toxicidade Aguda Oral (OECD TG 423)',
 'In vivo acute oral toxicity test classifying substances into GHS categories '
 'using a stepwise procedure with fixed doses. '
 'Typically requires 6 animals per limit dose; endpoint is mortality at fixed doses.',
 'Teste de toxicidade aguda oral in vivo que classifica substâncias em categorias GHS '
 'por procedimento escalonado com doses fixas. '
 'Tipicamente 6 animais por dose limite; endpoint é mortalidade em doses fixas.',
 'acute_toxicity acute toxic class ATC oral GHS category stepwise in vivo rat fixed dose reduction refinement general',
 '["reduction","refinement"]', 'acute_toxicity', 'general',
 'TG 423', NULL, 'OECD_TG', '["oral"]', FALSE),

('oecd-tg425-udp',
 'Up-and-Down Procedure (UDP) for Acute Oral Toxicity (OECD TG 425)',
 'Procedimento de Progressão Sequencial (UDP) para Toxicidade Aguda Oral (OECD TG 425)',
 'In vivo sequential acute oral toxicity test. '
 'Doses administered one at a time based on outcome of previous animal. '
 'Provides LD50 with confidence intervals using as few as 6 animals.',
 'Teste de toxicidade aguda oral in vivo com dosagem sequencial. '
 'Doses administradas individualmente com base no resultado do animal anterior. '
 'Fornece DL50 com intervalos de confiança com apenas 6 animais.',
 'acute_toxicity up-and-down procedure UDP oral LD50 sequential dosing confidence interval in vivo rat reduction refinement general',
 '["reduction","refinement"]', 'acute_toxicity', 'general',
 'TG 425', NULL, 'OECD_TG', '["oral"]', FALSE);

-- ── Validation contexts seed ────────────────────────────────────────────────
-- Seeded: brazil (RN 18/2014 confirmed) + oecd (TG number confirmed) + us (NICEATM only).
-- eu: [VERIFY] — Karynn confirms against EU Cosmetics Reg 1223/2009 and REACH Annex.
-- Methods postdating RN 18 (TG 492, 442C/D/E): oecd only; brazil row added when CONCEA adopts.
-- MAT brazil: [VERIFY] Farmacopeia chapter; seeded with notes flag.

INSERT INTO method_validation_contexts
    (method_id, study_domain, jurisdiction, validation_status, regulatory_body, regulatory_ref, regulatory_url, notes)
VALUES

-- oecd-tg439-epiderm
((SELECT id FROM methods WHERE slug='oecd-tg439-epiderm'),
 'general','brazil','validated','CONCEA','RN 18/2014 Art. 2',NULL,NULL),
((SELECT id FROM methods WHERE slug='oecd-tg439-epiderm'),
 'general','oecd','validated','OECD','TG 439',
 'https://www.oecd-ilibrary.org/environment/test-no-439-in-vitro-skin-irritation_9789264242845-en',NULL),

-- oecd-tg439-episkin
((SELECT id FROM methods WHERE slug='oecd-tg439-episkin'),
 'general','brazil','validated','CONCEA','RN 18/2014 Art. 2',NULL,NULL),
((SELECT id FROM methods WHERE slug='oecd-tg439-episkin'),
 'general','oecd','validated','OECD','TG 439',
 'https://www.oecd-ilibrary.org/environment/test-no-439-in-vitro-skin-irritation_9789264242845-en',NULL),

-- oecd-tg431-rhe-corrosion
((SELECT id FROM methods WHERE slug='oecd-tg431-rhe-corrosion'),
 'general','brazil','validated','CONCEA','RN 18/2014 Art. 2',NULL,NULL),
((SELECT id FROM methods WHERE slug='oecd-tg431-rhe-corrosion'),
 'general','oecd','validated','OECD','TG 431',
 'https://www.oecd-ilibrary.org/environment/test-no-431-in-vitro-skin-corrosion_9789264264618-en',NULL),

-- oecd-tg430-ter-corrosion
((SELECT id FROM methods WHERE slug='oecd-tg430-ter-corrosion'),
 'general','brazil','validated','CONCEA','RN 18/2014 Art. 2',NULL,NULL),
((SELECT id FROM methods WHERE slug='oecd-tg430-ter-corrosion'),
 'general','oecd','validated','OECD','TG 430',
 'https://www.oecd-ilibrary.org/environment/test-no-430-in-vitro-skin-corrosion_9789264264656-en',NULL),

-- oecd-tg435-membrane-barrier
((SELECT id FROM methods WHERE slug='oecd-tg435-membrane-barrier'),
 'general','brazil','validated','CONCEA','RN 18/2014 Art. 2',NULL,
 'Applicability limited to substances with pH < 2 or > 11.5.'),
((SELECT id FROM methods WHERE slug='oecd-tg435-membrane-barrier'),
 'general','oecd','validated','OECD','TG 435',
 'https://www.oecd-ilibrary.org/environment/test-no-435-in-vitro-membrane-barrier-test-method_9789264264694-en',NULL),

-- oecd-tg437-bcop
((SELECT id FROM methods WHERE slug='oecd-tg437-bcop'),
 'general','brazil','validated','CONCEA','RN 18/2014 Art. 2',NULL,NULL),
((SELECT id FROM methods WHERE slug='oecd-tg437-bcop'),
 'general','oecd','validated','OECD','TG 437',
 'https://www.oecd-ilibrary.org/environment/test-no-437-bovine-corneal-opacity-and-permeability-bcop-test-method_9789264264861-en',NULL),

-- oecd-tg438-ice
((SELECT id FROM methods WHERE slug='oecd-tg438-ice'),
 'general','brazil','validated','CONCEA','RN 18/2014 Art. 2',NULL,NULL),
((SELECT id FROM methods WHERE slug='oecd-tg438-ice'),
 'general','oecd','validated','OECD','TG 438',
 'https://www.oecd-ilibrary.org/environment/test-no-438-isolated-chicken-eye-ice-test-method_9789264264861-en',NULL),

-- oecd-tg492-rce — oecd only; no brazil row (postdates RN 18/2014)
((SELECT id FROM methods WHERE slug='oecd-tg492-rce'),
 'general','oecd','validated','OECD','TG 492',
 'https://www.oecd-ilibrary.org/environment/test-no-492-reconstructed-human-cornea-like-epithelium-rce-test-method_9789264242548-en',
 'TG 492 published 2019 — postdates RN 18/2014. Add brazil row when CONCEA adopts.'),

-- oecd-tg460-fluorescein-leakage
((SELECT id FROM methods WHERE slug='oecd-tg460-fluorescein-leakage'),
 'general','brazil','validated','CONCEA','RN 18/2014 Art. 2',NULL,NULL),
((SELECT id FROM methods WHERE slug='oecd-tg460-fluorescein-leakage'),
 'general','oecd','validated','OECD','TG 460',
 'https://www.oecd-ilibrary.org/environment/test-no-460-fluorescein-leakage-test-method_9789264185951-en',NULL),

-- oecd-tg442c-dpra — oecd only (postdates RN 18)
((SELECT id FROM methods WHERE slug='oecd-tg442c-dpra'),
 'general','oecd','validated','OECD','TG 442C',
 'https://www.oecd-ilibrary.org/environment/test-no-442c-in-chemico-skin-sensitisation_9789264229709-en',
 'TG 442C published 2015 — postdates RN 18/2014. Add brazil row when CONCEA adopts.'),

-- oecd-tg442d-keratinosens — oecd only
((SELECT id FROM methods WHERE slug='oecd-tg442d-keratinosens'),
 'general','oecd','validated','OECD','TG 442D',
 'https://www.oecd-ilibrary.org/environment/test-no-442d-in-vitro-skin-sensitisation_9789264229822-en',
 'TG 442D published 2015 — postdates RN 18/2014. Add brazil row when CONCEA adopts.'),

-- oecd-tg442e-hclat — oecd only
((SELECT id FROM methods WHERE slug='oecd-tg442e-hclat'),
 'general','oecd','validated','OECD','TG 442E',
 'https://www.oecd-ilibrary.org/environment/test-no-442e-in-vitro-skin-sensitisation_9789264264359-en',
 'TG 442E published 2017 — postdates RN 18/2014. Add brazil row when CONCEA adopts.'),

-- oecd-tg429-llna
((SELECT id FROM methods WHERE slug='oecd-tg429-llna'),
 'general','brazil','validated','CONCEA','RN 18/2014 Art. 2',NULL,NULL),
((SELECT id FROM methods WHERE slug='oecd-tg429-llna'),
 'general','oecd','validated','OECD','TG 429',
 'https://www.oecd-ilibrary.org/environment/test-no-429-skin-sensitisation_9789264071100-en',NULL),

-- oecd-tg442a-llna-da
((SELECT id FROM methods WHERE slug='oecd-tg442a-llna-da'),
 'general','brazil','validated','CONCEA','RN 18/2014 Art. 2',NULL,NULL),
((SELECT id FROM methods WHERE slug='oecd-tg442a-llna-da'),
 'general','oecd','validated','OECD','TG 442A',
 'https://www.oecd-ilibrary.org/environment/test-no-442a-skin-sensitization-local-lymph-node-assay-da_9789264090972-en',NULL),

-- oecd-tg442b-llna-brdu
((SELECT id FROM methods WHERE slug='oecd-tg442b-llna-brdu'),
 'general','brazil','validated','CONCEA','RN 18/2014 Art. 2',NULL,NULL),
((SELECT id FROM methods WHERE slug='oecd-tg442b-llna-brdu'),
 'general','oecd','validated','OECD','TG 442B',
 'https://www.oecd-ilibrary.org/environment/test-no-442b-skin-sensitization-local-lymph-node-assay-brdu-elisa_9789264090996-en',NULL),

-- oecd-tg432-3t3nru
((SELECT id FROM methods WHERE slug='oecd-tg432-3t3nru'),
 'general','brazil','validated','CONCEA','RN 18/2014 Art. 2',NULL,NULL),
((SELECT id FROM methods WHERE slug='oecd-tg432-3t3nru'),
 'general','oecd','validated','OECD','TG 432',
 'https://www.oecd-ilibrary.org/environment/test-no-432-in-vitro-3t3-nru-phototoxicity-test_9789264071162-en',NULL),

-- oecd-tg428-skin-absorption-vitro
((SELECT id FROM methods WHERE slug='oecd-tg428-skin-absorption-vitro'),
 'general','brazil','validated','CONCEA','RN 18/2014 Art. 2',NULL,NULL),
((SELECT id FROM methods WHERE slug='oecd-tg428-skin-absorption-vitro'),
 'general','oecd','validated','OECD','TG 428',
 'https://www.oecd-ilibrary.org/environment/test-no-428-skin-absorption-in-vitro-method_9789264071087-en',NULL),

-- oecd-tg471-ames
((SELECT id FROM methods WHERE slug='oecd-tg471-ames'),
 'general','brazil','validated','CONCEA','RN 18/2014 Art. 2',NULL,NULL),
((SELECT id FROM methods WHERE slug='oecd-tg471-ames'),
 'general','oecd','validated','OECD','TG 471',
 'https://www.oecd-ilibrary.org/environment/test-no-471-bacterial-reverse-mutation-test_9789264071247-en',NULL),

-- oecd-tg476-hprt
((SELECT id FROM methods WHERE slug='oecd-tg476-hprt'),
 'general','brazil','validated','CONCEA','RN 18/2014 Art. 2',NULL,NULL),
((SELECT id FROM methods WHERE slug='oecd-tg476-hprt'),
 'general','oecd','validated','OECD','TG 476',
 'https://www.oecd-ilibrary.org/environment/test-no-476-in-vitro-mammalian-cell-gene-mutation-tests-using-the-hprt-and-xprt-genes_9789264264809-en',NULL),

-- oecd-tg487-micronucleus
((SELECT id FROM methods WHERE slug='oecd-tg487-micronucleus'),
 'general','brazil','validated','CONCEA','RN 18/2014 Art. 2',NULL,NULL),
((SELECT id FROM methods WHERE slug='oecd-tg487-micronucleus'),
 'general','oecd','validated','OECD','TG 487',
 'https://www.oecd-ilibrary.org/environment/test-no-487-in-vitro-mammalian-cell-micronucleus-test_9789264264861-en',NULL),

-- mat-monocyte-activation
((SELECT id FROM methods WHERE slug='mat-monocyte-activation'),
 'general','brazil','validated','ANVISA',NULL,NULL,
 '[VERIFY] Confirm Farmacopeia Brasileira chapter reference and regulatory_body (ANVISA vs CONCEA). '
 'Update regulatory_ref and regulatory_url after confirmation.'),

-- niceatm-cytotox-basal-barranco
((SELECT id FROM methods WHERE slug='niceatm-cytotox-basal-barranco'),
 'general','brazil','accepted','CONCEA','RN 18/2014 Art. 2 VI-d via OECD GD 129',NULL,
 'Accepted via GD 129 reference in RN 18. Confirm article and jurisdiction_notes.'),
((SELECT id FROM methods WHERE slug='niceatm-cytotox-basal-barranco'),
 'general','oecd','accepted','OECD','GD 129',NULL,NULL),
((SELECT id FROM methods WHERE slug='niceatm-cytotox-basal-barranco'),
 'general','us','validated','ICCVAM',NULL,'https://ntp.niehs.nih.gov/go/niceatm',NULL),

-- oecd-tg420-fixed-dose
((SELECT id FROM methods WHERE slug='oecd-tg420-fixed-dose'),
 'general','brazil','validated','CONCEA','RN 18/2014 Art. 2',NULL,NULL),
((SELECT id FROM methods WHERE slug='oecd-tg420-fixed-dose'),
 'general','oecd','validated','OECD','TG 420',
 'https://www.oecd-ilibrary.org/environment/test-no-420-acute-oral-toxicity-fixed-dose-procedure_9789264070943-en',NULL),

-- oecd-tg423-atc
((SELECT id FROM methods WHERE slug='oecd-tg423-atc'),
 'general','brazil','validated','CONCEA','RN 18/2014 Art. 2',NULL,NULL),
((SELECT id FROM methods WHERE slug='oecd-tg423-atc'),
 'general','oecd','validated','OECD','TG 423',
 'https://www.oecd-ilibrary.org/environment/test-no-423-acute-oral-toxicity-acute-toxic-class-method_9789264071001-en',NULL),

-- oecd-tg425-udp
((SELECT id FROM methods WHERE slug='oecd-tg425-udp'),
 'general','brazil','validated','CONCEA','RN 18/2014 Art. 2',NULL,NULL),
((SELECT id FROM methods WHERE slug='oecd-tg425-udp'),
 'general','oecd','validated','OECD','TG 425',
 'https://www.oecd-ilibrary.org/environment/test-no-425-acute-oral-toxicity-up-and-down-procedure_9789264071049-en',NULL);

-- ── Keywords ────────────────────────────────────────────────────────────────

INSERT INTO method_keywords (method_id, keyword, language) VALUES
((SELECT id FROM methods WHERE slug='oecd-tg439-epiderm'),'epiderm','en'),
((SELECT id FROM methods WHERE slug='oecd-tg439-epiderm'),'reconstructed human epidermis','en'),
((SELECT id FROM methods WHERE slug='oecd-tg439-epiderm'),'RHE','en'),
((SELECT id FROM methods WHERE slug='oecd-tg439-epiderm'),'epiderme humana reconstituída','pt'),
((SELECT id FROM methods WHERE slug='oecd-tg439-epiderm'),'irritação cutânea in vitro','pt'),
((SELECT id FROM methods WHERE slug='oecd-tg439-episkin'),'episkin','en'),
((SELECT id FROM methods WHERE slug='oecd-tg439-episkin'),'reconstructed human epidermis','en'),
((SELECT id FROM methods WHERE slug='oecd-tg439-episkin'),'epiderme reconstituída','pt'),
((SELECT id FROM methods WHERE slug='oecd-tg431-rhe-corrosion'),'skin corrosion RHE','en'),
((SELECT id FROM methods WHERE slug='oecd-tg431-rhe-corrosion'),'corrosão cutânea epiderme reconstituída','pt'),
((SELECT id FROM methods WHERE slug='oecd-tg430-ter-corrosion'),'TER','en'),
((SELECT id FROM methods WHERE slug='oecd-tg430-ter-corrosion'),'transcutaneous electrical resistance','en'),
((SELECT id FROM methods WHERE slug='oecd-tg430-ter-corrosion'),'resistência elétrica transcutânea','pt'),
((SELECT id FROM methods WHERE slug='oecd-tg435-membrane-barrier'),'CORROSITEX','en'),
((SELECT id FROM methods WHERE slug='oecd-tg435-membrane-barrier'),'membrane barrier test','en'),
((SELECT id FROM methods WHERE slug='oecd-tg435-membrane-barrier'),'barreira de membrana','pt'),
((SELECT id FROM methods WHERE slug='oecd-tg437-bcop'),'BCOP','en'),
((SELECT id FROM methods WHERE slug='oecd-tg437-bcop'),'bovine corneal opacity permeability','en'),
((SELECT id FROM methods WHERE slug='oecd-tg437-bcop'),'córnea bovina opacidade permeabilidade','pt'),
((SELECT id FROM methods WHERE slug='oecd-tg437-bcop'),'draize eye alternative','en'),
((SELECT id FROM methods WHERE slug='oecd-tg438-ice'),'ICE','en'),
((SELECT id FROM methods WHERE slug='oecd-tg438-ice'),'isolated chicken eye','en'),
((SELECT id FROM methods WHERE slug='oecd-tg438-ice'),'olho de galinha isolado','pt'),
((SELECT id FROM methods WHERE slug='oecd-tg492-rce'),'RCE','en'),
((SELECT id FROM methods WHERE slug='oecd-tg492-rce'),'reconstructed human cornea','en'),
((SELECT id FROM methods WHERE slug='oecd-tg492-rce'),'córnea humana reconstituída','pt'),
((SELECT id FROM methods WHERE slug='oecd-tg460-fluorescein-leakage'),'fluorescein leakage','en'),
((SELECT id FROM methods WHERE slug='oecd-tg460-fluorescein-leakage'),'FL test MDCK','en'),
((SELECT id FROM methods WHERE slug='oecd-tg460-fluorescein-leakage'),'extravasamento fluoresceína','pt'),
((SELECT id FROM methods WHERE slug='oecd-tg442c-dpra'),'DPRA','en'),
((SELECT id FROM methods WHERE slug='oecd-tg442c-dpra'),'direct peptide reactivity haptenation','en'),
((SELECT id FROM methods WHERE slug='oecd-tg442c-dpra'),'reatividade peptídeos','pt'),
((SELECT id FROM methods WHERE slug='oecd-tg442d-keratinosens'),'KeratinoSens ARE-Nrf2','en'),
((SELECT id FROM methods WHERE slug='oecd-tg442d-keratinosens'),'queratinócito Nrf2 luciferase','pt'),
((SELECT id FROM methods WHERE slug='oecd-tg442e-hclat'),'h-CLAT THP-1 CD54 CD86','en'),
((SELECT id FROM methods WHERE slug='oecd-tg442e-hclat'),'ativação monócitos sensibilização','pt'),
((SELECT id FROM methods WHERE slug='oecd-tg429-llna'),'LLNA EC3','en'),
((SELECT id FROM methods WHERE slug='oecd-tg429-llna'),'local lymph node assay','en'),
((SELECT id FROM methods WHERE slug='oecd-tg429-llna'),'ensaio linfonodo local','pt'),
((SELECT id FROM methods WHERE slug='oecd-tg442a-llna-da'),'LLNA DA non-radioactive ATP','en'),
((SELECT id FROM methods WHERE slug='oecd-tg442a-llna-da'),'LLNA não radioativo','pt'),
((SELECT id FROM methods WHERE slug='oecd-tg442b-llna-brdu'),'LLNA BrdU ELISA','en'),
((SELECT id FROM methods WHERE slug='oecd-tg442b-llna-brdu'),'BrdU ELISA sensibilização','pt'),
((SELECT id FROM methods WHERE slug='oecd-tg432-3t3nru'),'3T3 NRU PIF MPE','en'),
((SELECT id FROM methods WHERE slug='oecd-tg432-3t3nru'),'fototoxicidade vermelho neutro','pt'),
((SELECT id FROM methods WHERE slug='oecd-tg428-skin-absorption-vitro'),'Franz diffusion cell','en'),
((SELECT id FROM methods WHERE slug='oecd-tg428-skin-absorption-vitro'),'absorção percutânea Franz','pt'),
((SELECT id FROM methods WHERE slug='oecd-tg471-ames'),'Ames test Salmonella','en'),
((SELECT id FROM methods WHERE slug='oecd-tg471-ames'),'teste de Ames mutagenicidade','pt'),
((SELECT id FROM methods WHERE slug='oecd-tg476-hprt'),'HPRT gene mutation CHO V79','en'),
((SELECT id FROM methods WHERE slug='oecd-tg476-hprt'),'mutação gênica célula mamífero','pt'),
((SELECT id FROM methods WHERE slug='oecd-tg487-micronucleus'),'micronucleus MNvit clastogenicity','en'),
((SELECT id FROM methods WHERE slug='oecd-tg487-micronucleus'),'micronúcleo in vitro clastogenicidade','pt'),
((SELECT id FROM methods WHERE slug='mat-monocyte-activation'),'MAT monocyte activation pyrogen','en'),
((SELECT id FROM methods WHERE slug='mat-monocyte-activation'),'teste ativação monócitos pirogênio','pt'),
((SELECT id FROM methods WHERE slug='mat-monocyte-activation'),'rabbit pyrogen test alternative RPT','en'),
((SELECT id FROM methods WHERE slug='niceatm-cytotox-basal-barranco'),'basal cytotoxicity LD50 starting dose','en'),
((SELECT id FROM methods WHERE slug='niceatm-cytotox-basal-barranco'),'citotoxicidade basal dose inicial DL50','pt'),
((SELECT id FROM methods WHERE slug='oecd-tg420-fixed-dose'),'fixed dose procedure FDP GHS','en'),
((SELECT id FROM methods WHERE slug='oecd-tg420-fixed-dose'),'dose fixa toxicidade aguda oral','pt'),
((SELECT id FROM methods WHERE slug='oecd-tg423-atc'),'acute toxic class ATC','en'),
((SELECT id FROM methods WHERE slug='oecd-tg423-atc'),'classe tóxica aguda','pt'),
((SELECT id FROM methods WHERE slug='oecd-tg425-udp'),'up-and-down procedure UDP LD50','en'),
((SELECT id FROM methods WHERE slug='oecd-tg425-udp'),'progressão sequencial DL50','pt');
