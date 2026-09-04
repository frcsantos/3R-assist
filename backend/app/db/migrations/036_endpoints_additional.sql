-- =============================================================================
-- Migration 036: seed additional endpoints vocabulary codes
-- =============================================================================

INSERT INTO endpoints (code, name, description, sort_order, active)
VALUES
(
    'reproductive_toxicity',
    '{"en-us":"Reproductive and developmental toxicity","pt-br":"Toxicidade reprodutiva e do desenvolvimento"}'::jsonb,
    '{"en-us":"Effects on reproductive function, fertility, embryonic and developmental outcomes, including combined screening studies.","pt-br":"Efeitos sobre função reprodutiva, fertilidade e desenvolvimento embrionário, incluindo estudos combinados de triagem."}'::jsonb,
    100,
    TRUE
),
(
    'endocrine_activity',
    '{"en-us":"Endocrine activity","pt-br":"Atividade endócrina"}'::jsonb,
    '{"en-us":"Estrogenic, androgenic and steroidogenic activity relevant to the assessment of endocrine disruption.","pt-br":"Atividades estrogênica, androgênica e esteroidogênica relevantes para a avaliação de desregulação endócrina."}'::jsonb,
    110,
    TRUE
),
(
    'photoreactivity',
    '{"en-us":"Photoreactivity","pt-br":"Fotorreatividade"}'::jsonb,
    '{"en-us":"Chemical reactivity under light exposure, including reactive oxygen species generation and other indicators of photoreactive potential.","pt-br":"Reatividade química sob exposição à luz, incluindo geração de espécies reativas de oxigênio e outros indicadores de potencial fotorreativo."}'::jsonb,
    120,
    TRUE
),
(
    'aquatic_toxicity',
    '{"en-us":"Aquatic toxicity","pt-br":"Toxicidade aquática"}'::jsonb,
    '{"en-us":"Adverse effects on aquatic organisms, including acute toxicity and effects on fish embryos and early life stages.","pt-br":"Efeitos adversos sobre organismos aquáticos, incluindo toxicidade aguda e efeitos sobre embriões e estágios iniciais de peixes."}'::jsonb,
    130,
    TRUE
),
(
    'toxicokinetics',
    '{"en-us":"Toxicokinetics","pt-br":"Toxicocinética"}'::jsonb,
    '{"en-us":"Absorption, metabolism, intrinsic clearance and other kinetic parameters relevant to chemical safety assessment.","pt-br":"Absorção, metabolismo, depuração intrínseca e outros parâmetros cinéticos relevantes para a avaliação de segurança química."}'::jsonb,
    140,
    TRUE
),
(
    'bacterial_endotoxin',
    '{"en-us":"Bacterial endotoxin","pt-br":"Endotoxinas bacterianas"}'::jsonb,
    '{"en-us":"Detection or quantification of bacterial endotoxin activity in products and samples.","pt-br":"Detecção ou quantificação da atividade de endotoxinas bacterianas em produtos e amostras."}'::jsonb,
    150,
    TRUE
),
(
    'rabies_diagnosis',
    '{"en-us":"Rabies diagnosis","pt-br":"Diagnóstico da raiva"}'::jsonb,
    '{"en-us":"Detection of rabies virus antigen, nucleic acid or infectious virus in animal samples.","pt-br":"Detecção de antígeno, ácido nucleico ou vírus infeccioso da raiva em amostras animais."}'::jsonb,
    160,
    TRUE
)
ON CONFLICT (code) DO UPDATE
SET
    name = EXCLUDED.name,
    description = EXCLUDED.description,
    sort_order = EXCLUDED.sort_order,
    active = EXCLUDED.active,
    updated_at = NOW();
