-- =============================================================================
-- Migration 054: replace endpoints catalogue + external_oht_codes
-- Remap methods.endpoints, regulations.regulatory_endpoints, route_endpoints
-- from previous slugs to the new hierarchy ids.
-- =============================================================================

BEGIN;

ALTER TABLE endpoints
  ADD COLUMN IF NOT EXISTS external_oht_codes JSONB;

ALTER TABLE endpoints
  DROP CONSTRAINT IF EXISTS fk_endpoints_parent;

ALTER TABLE route_endpoints
  DROP CONSTRAINT IF EXISTS route_endpoints_endpoint_id_fkey;

CREATE TEMP TABLE endpoint_slug_map (
  old_slug TEXT PRIMARY KEY,
  new_id INTEGER NOT NULL
) ;

INSERT INTO endpoint_slug_map (old_slug, new_id) VALUES
  ('toxicokinetics', 1),
  ('toxicokinetic-properties', 1),
  ('absorption', 2),
  ('skin-absorption', 3),
  ('dermal-absorption', 3),
  ('distribution', 4),
  ('metabolism', 5),
  ('excretion', 6),
  ('skin-irritation', 10),
  ('skin-corrosion', 11),
  ('phototoxicity', 12),
  ('ocular-irritation', 14),
  ('eye-irritation', 14),
  ('acute-toxicity', 17),
  ('acute-systemic-toxicity', 17),
  ('skin-sensitisation', 20),
  ('genotoxicity', 22),
  ('reproductive-toxicity', 25),
  ('endocrine-activity', 32),
  ('photoreactivity', 37),
  ('aquatic-toxicity', 40),
  ('pyrogenicity', 49),
  ('bacterial-endotoxin', 50),
  ('bacterial-endotoxins', 50),
  ('rabies-diagnosis', 54);

CREATE TEMP TABLE endpoint_id_map AS
SELECT e.id AS old_id, m.new_id
FROM endpoints e
JOIN endpoint_slug_map m ON m.old_slug = e.slug;

UPDATE methods m
SET endpoints = sub.ids
FROM (
  SELECT m2.id,
         COALESCE(
           array_agg(map.new_id ORDER BY u.ord)
             FILTER (WHERE map.new_id IS NOT NULL),
           '{}'::int[]
         ) AS ids
  FROM methods m2
  LEFT JOIN LATERAL unnest(COALESCE(m2.endpoints, '{}'::int[]))
    WITH ORDINALITY AS u(old_id, ord) ON TRUE
  LEFT JOIN endpoint_id_map map ON map.old_id = u.old_id
  GROUP BY m2.id
) sub
WHERE m.id = sub.id;

UPDATE regulations r
SET regulatory_endpoints = sub.ids
FROM (
  SELECT r2.id,
         CASE
           WHEN r2.regulatory_endpoints IS NULL THEN NULL
           ELSE COALESCE(
             array_agg(map.new_id ORDER BY u.ord)
               FILTER (WHERE map.new_id IS NOT NULL),
             '{}'::int[]
           )
         END AS ids
  FROM regulations r2
  LEFT JOIN LATERAL unnest(COALESCE(r2.regulatory_endpoints, '{}'::int[]))
    WITH ORDINALITY AS u(old_id, ord) ON TRUE
  LEFT JOIN endpoint_id_map map ON map.old_id = u.old_id
  GROUP BY r2.id, r2.regulatory_endpoints
) sub
WHERE r.id = sub.id;

DELETE FROM route_endpoints re
WHERE NOT EXISTS (
  SELECT 1 FROM endpoint_id_map map WHERE map.old_id = re.endpoint_id
);

CREATE TEMP TABLE route_endpoints_mapped AS
SELECT DISTINCT re.route_code, map.new_id AS endpoint_id
FROM route_endpoints re
JOIN endpoint_id_map map ON map.old_id = re.endpoint_id;

DELETE FROM route_endpoints;

INSERT INTO route_endpoints (route_code, endpoint_id)
SELECT route_code, endpoint_id FROM route_endpoints_mapped;

UPDATE endpoints SET parent_id = NULL;
DELETE FROM endpoints;

INSERT INTO endpoints (
  id, code, slug, parent_id, external_oht_codes, name, description,
  sort_order, active
) VALUES
  (1, '1', 'toxicokinetic-properties', NULL, '["58"]'::jsonb, '{"en-us": "Toxicokinetic properties", "pt-br": "Propriedades toxicocinéticas"}'::jsonb, '{"en-us": "Processes describing the absorption, distribution, metabolism and excretion of a substance.", "pt-br": "Processos que descrevem a absorção, distribuição, metabolismo e excreção de uma substância."}'::jsonb, 1, TRUE),
  (2, '1.1', 'absorption', 1, '["58"]'::jsonb, '{"en-us": "Absorption", "pt-br": "Absorção"}'::jsonb, '{"en-us": "Entry of a substance into an organism from the site of exposure.", "pt-br": "Entrada de uma substância no organismo a partir do local de exposição."}'::jsonb, 2, TRUE),
  (3, '1.1.1', 'dermal-absorption', 2, '["59"]'::jsonb, '{"en-us": "Dermal absorption", "pt-br": "Absorção cutânea"}'::jsonb, '{"en-us": "Passage of a substance through the skin into local tissues or systemic circulation.", "pt-br": "Passagem de uma substância através da pele para tecidos locais ou para a circulação sistêmica."}'::jsonb, 3, TRUE),
  (4, '1.2', 'distribution', 1, '["58"]'::jsonb, '{"en-us": "Distribution", "pt-br": "Distribuição"}'::jsonb, '{"en-us": "Transport and partitioning of a substance among tissues and biological compartments.", "pt-br": "Transporte e distribuição de uma substância entre tecidos e compartimentos biológicos."}'::jsonb, 4, TRUE),
  (5, '1.3', 'metabolism', 1, '["58"]'::jsonb, '{"en-us": "Metabolism", "pt-br": "Metabolismo"}'::jsonb, '{"en-us": "Biological transformation of a substance into metabolites.", "pt-br": "Transformação biológica de uma substância em metabólitos."}'::jsonb, 5, TRUE),
  (6, '1.4', 'excretion', 1, '["58"]'::jsonb, '{"en-us": "Excretion", "pt-br": "Excreção"}'::jsonb, '{"en-us": "Removal of a substance or its metabolites from an organism.", "pt-br": "Eliminação de uma substância ou de seus metabólitos do organismo."}'::jsonb, 6, TRUE),
  (7, '2', 'human-health-effects', NULL, '[]'::jsonb, '{"en-us": "Human health effects", "pt-br": "Efeitos sobre a saúde humana"}'::jsonb, '{"en-us": "Adverse biological effects relevant to human health hazard assessment.", "pt-br": "Efeitos biológicos adversos relevantes para a avaliação de perigos à saúde humana."}'::jsonb, 7, TRUE),
  (8, '2.1', 'local-effects', 7, '["64", "65"]'::jsonb, '{"en-us": "Local effects", "pt-br": "Efeitos locais"}'::jsonb, '{"en-us": "Adverse effects occurring primarily at or near the site of contact.", "pt-br": "Efeitos adversos que ocorrem principalmente no local de contato ou próximo a ele."}'::jsonb, 8, TRUE),
  (9, '2.1.1', 'skin-effects', 8, '["64"]'::jsonb, '{"en-us": "Skin effects", "pt-br": "Efeitos cutâneos"}'::jsonb, '{"en-us": "Local adverse effects involving the skin.", "pt-br": "Efeitos adversos locais que envolvem a pele."}'::jsonb, 9, TRUE),
  (10, '2.1.1.1', 'skin-irritation', 9, '["64"]'::jsonb, '{"en-us": "Skin irritation", "pt-br": "Irritação cutânea"}'::jsonb, '{"en-us": "Reversible inflammatory damage to the skin following exposure.", "pt-br": "Dano inflamatório reversível à pele após a exposição."}'::jsonb, 10, TRUE),
  (11, '2.1.1.2', 'skin-corrosion', 9, '["64"]'::jsonb, '{"en-us": "Skin corrosion", "pt-br": "Corrosão cutânea"}'::jsonb, '{"en-us": "Irreversible destruction of skin tissue following exposure.", "pt-br": "Destruição irreversível do tecido cutâneo após a exposição."}'::jsonb, 11, TRUE),
  (12, '2.1.1.3', 'phototoxicity', 9, '["78"]'::jsonb, '{"en-us": "Phototoxicity", "pt-br": "Fototoxicidade"}'::jsonb, '{"en-us": "Adverse effect produced when exposure to a substance is combined with light.", "pt-br": "Efeito adverso produzido quando a exposição a uma substância é combinada com a exposição à luz."}'::jsonb, 12, TRUE),
  (13, '2.1.2', 'eye-effects', 8, '["65"]'::jsonb, '{"en-us": "Eye effects", "pt-br": "Efeitos oculares"}'::jsonb, '{"en-us": "Local adverse effects involving the eye or ocular surface.", "pt-br": "Efeitos adversos locais que envolvem o olho ou a superfície ocular."}'::jsonb, 13, TRUE),
  (14, '2.1.2.1', 'eye-irritation', 13, '["65"]'::jsonb, '{"en-us": "Eye irritation", "pt-br": "Irritação ocular"}'::jsonb, '{"en-us": "Ocular changes that are fully reversible within the applicable observation period.", "pt-br": "Alterações oculares completamente reversíveis dentro do período de observação aplicável."}'::jsonb, 14, TRUE),
  (15, '2.1.2.2', 'serious-eye-damage', 13, '["65"]'::jsonb, '{"en-us": "Serious eye damage", "pt-br": "Danos oculares graves"}'::jsonb, '{"en-us": "Ocular tissue damage or serious vision impairment that is not fully reversible within the applicable observation period.", "pt-br": "Dano ao tecido ocular ou comprometimento grave da visão que não é completamente reversível dentro do período de observação aplicável."}'::jsonb, 15, TRUE),
  (16, '2.2', 'systemic-toxicity', 7, '[]'::jsonb, '{"en-us": "Systemic toxicity", "pt-br": "Toxicidade sistêmica"}'::jsonb, '{"en-us": "Adverse effects occurring after a substance reaches tissues or organs beyond the initial contact site.", "pt-br": "Efeitos adversos que ocorrem após a substância atingir tecidos ou órgãos além do local inicial de contato."}'::jsonb, 16, TRUE),
  (17, '2.2.1', 'acute-systemic-toxicity', 16, '["60", "61", "62", "63"]'::jsonb, '{"en-us": "Acute systemic toxicity", "pt-br": "Toxicidade sistêmica aguda"}'::jsonb, '{"en-us": "Adverse systemic effects resulting from a single exposure or multiple exposures over a short period.", "pt-br": "Efeitos sistêmicos adversos resultantes de uma única exposição ou de múltiplas exposições durante um período curto."}'::jsonb, 17, TRUE),
  (18, '2.2.2', 'repeated-dose-toxicity', 16, '["67", "68", "69"]'::jsonb, '{"en-us": "Repeated-dose toxicity", "pt-br": "Toxicidade por doses repetidas"}'::jsonb, '{"en-us": "Adverse effects resulting from repeated exposure over a specified period.", "pt-br": "Efeitos adversos resultantes de exposições repetidas durante um período determinado."}'::jsonb, 18, TRUE),
  (19, '2.3', 'sensitisation', 7, '["66-1"]'::jsonb, '{"en-us": "Sensitisation", "pt-br": "Sensibilização"}'::jsonb, '{"en-us": "Acquisition of an increased biological response following previous exposure to a substance.", "pt-br": "Aquisição de uma resposta biológica aumentada após exposição prévia a uma substância."}'::jsonb, 19, TRUE),
  (20, '2.3.1', 'skin-sensitisation', 19, '["66-1"]'::jsonb, '{"en-us": "Skin sensitisation", "pt-br": "Sensibilização cutânea"}'::jsonb, '{"en-us": "Allergic response elicited in the skin following prior induction by a substance.", "pt-br": "Resposta alérgica manifestada na pele após sensibilização prévia por uma substância."}'::jsonb, 20, TRUE),
  (21, '2.4', 'genetic-effects', 7, '["70", "71"]'::jsonb, '{"en-us": "Genetic effects", "pt-br": "Efeitos genéticos"}'::jsonb, '{"en-us": "Adverse effects involving DNA, chromosomes or the transmission of genetic information.", "pt-br": "Efeitos adversos que envolvem o DNA, os cromossomos ou a transmissão de informação genética."}'::jsonb, 21, TRUE),
  (22, '2.4.1', 'genotoxicity', 21, '["70", "71"]'::jsonb, '{"en-us": "Genotoxicity", "pt-br": "Genotoxicidade"}'::jsonb, '{"en-us": "Capacity to damage DNA, chromosomes or related cellular structures and processes.", "pt-br": "Capacidade de danificar o DNA, os cromossomos ou estruturas e processos celulares relacionados."}'::jsonb, 22, TRUE),
  (23, '2.4.1.1', 'mutagenicity', 22, '["70", "71"]'::jsonb, '{"en-us": "Mutagenicity", "pt-br": "Mutagenicidade"}'::jsonb, '{"en-us": "Capacity to cause permanent and potentially heritable changes in genetic material.", "pt-br": "Capacidade de causar alterações permanentes e potencialmente hereditárias no material genético."}'::jsonb, 23, TRUE),
  (24, '2.5', 'reproductive-developmental-effects', 7, '["73", "74"]'::jsonb, '{"en-us": "Reproductive and developmental effects", "pt-br": "Efeitos reprodutivos e do desenvolvimento"}'::jsonb, '{"en-us": "Adverse effects on reproduction, fertility, pregnancy or development of offspring.", "pt-br": "Efeitos adversos sobre reprodução, fertilidade, gestação ou desenvolvimento da descendência."}'::jsonb, 24, TRUE),
  (25, '2.5.1', 'reproductive-toxicity', 24, '["73"]'::jsonb, '{"en-us": "Reproductive toxicity", "pt-br": "Toxicidade reprodutiva"}'::jsonb, '{"en-us": "Adverse effects on sexual function, fertility, pregnancy or reproductive performance.", "pt-br": "Efeitos adversos sobre função sexual, fertilidade, gestação ou desempenho reprodutivo."}'::jsonb, 25, TRUE),
  (26, '2.5.2', 'developmental-toxicity', 24, '["74"]'::jsonb, '{"en-us": "Developmental toxicity", "pt-br": "Toxicidade do desenvolvimento"}'::jsonb, '{"en-us": "Adverse effects on an organism resulting from exposure before conception, during prenatal development or during postnatal development.", "pt-br": "Efeitos adversos sobre um organismo resultantes de exposição antes da concepção, durante o desenvolvimento pré-natal ou durante o desenvolvimento pós-natal."}'::jsonb, 26, TRUE),
  (27, '2.6', 'other-health-effects', 7, '[]'::jsonb, '{"en-us": "Other health effects", "pt-br": "Outros efeitos sobre a saúde"}'::jsonb, '{"en-us": "Human-health effect domains not classified under the preceding groups.", "pt-br": "Domínios de efeitos sobre a saúde humana não classificados nos grupos anteriores."}'::jsonb, 27, TRUE),
  (28, '2.6.1', 'carcinogenicity', 27, '["72"]'::jsonb, '{"en-us": "Carcinogenicity", "pt-br": "Carcinogenicidade"}'::jsonb, '{"en-us": "Capacity to cause or increase the incidence of malignant or benign neoplasms.", "pt-br": "Capacidade de causar ou aumentar a incidência de neoplasias malignas ou benignas."}'::jsonb, 28, TRUE),
  (29, '2.6.2', 'neurotoxicity', 27, '["78"]'::jsonb, '{"en-us": "Neurotoxicity", "pt-br": "Neurotoxicidade"}'::jsonb, '{"en-us": "Adverse effects on the structure or function of the nervous system.", "pt-br": "Efeitos adversos sobre a estrutura ou o funcionamento do sistema nervoso."}'::jsonb, 29, TRUE),
  (30, '2.6.3', 'immunotoxicity', 27, '["78"]'::jsonb, '{"en-us": "Immunotoxicity", "pt-br": "Imunotoxicidade"}'::jsonb, '{"en-us": "Adverse effects on the structure, regulation or function of the immune system.", "pt-br": "Efeitos adversos sobre a estrutura, regulação ou funcionamento do sistema imunológico."}'::jsonb, 30, TRUE),
  (31, '3', 'biological-mechanistic-activities', NULL, '["78", "201"]'::jsonb, '{"en-us": "Biological and mechanistic activities", "pt-br": "Atividades biológicas e mecanísticas"}'::jsonb, '{"en-us": "Biological activities or mechanistic events that may contribute to, precede or predict adverse outcomes.", "pt-br": "Atividades biológicas ou eventos mecanísticos que podem contribuir para, anteceder ou prever desfechos adversos."}'::jsonb, 31, TRUE),
  (32, '3.1', 'endocrine-activity', 31, '["78", "201"]'::jsonb, '{"en-us": "Endocrine activity", "pt-br": "Atividade endócrina"}'::jsonb, '{"en-us": "Interaction with or alteration of endocrine signalling, hormone synthesis, transport, metabolism or action.", "pt-br": "Interação com ou alteração da sinalização endócrina ou da síntese, transporte, metabolismo ou ação hormonal."}'::jsonb, 32, TRUE),
  (33, '3.1.1', 'estrogenic-activity', 32, '["78", "201"]'::jsonb, '{"en-us": "Estrogenic activity", "pt-br": "Atividade estrogênica"}'::jsonb, '{"en-us": "Activity mediated by estrogen receptors or other components of estrogen signalling.", "pt-br": "Atividade mediada por receptores de estrogênio ou por outros componentes da sinalização estrogênica."}'::jsonb, 33, TRUE),
  (34, '3.1.2', 'androgenic-activity', 32, '["78", "201"]'::jsonb, '{"en-us": "Androgenic activity", "pt-br": "Atividade androgênica"}'::jsonb, '{"en-us": "Activity mediated by androgen receptors or other components of androgen signalling.", "pt-br": "Atividade mediada por receptores de androgênio ou por outros componentes da sinalização androgênica."}'::jsonb, 34, TRUE),
  (35, '3.1.3', 'thyroid-related-activity', 32, '["78", "201"]'::jsonb, '{"en-us": "Thyroid-related activity", "pt-br": "Atividade relacionada à tireoide"}'::jsonb, '{"en-us": "Activity affecting thyroid hormone synthesis, transport, metabolism, receptor signalling or regulation.", "pt-br": "Atividade que afeta a síntese, transporte, metabolismo, sinalização receptorial ou regulação dos hormônios tireoidianos."}'::jsonb, 35, TRUE),
  (36, '3.1.4', 'steroidogenesis-activity', 32, '["78", "201"]'::jsonb, '{"en-us": "Steroidogenesis activity", "pt-br": "Atividade de esteroidogênese"}'::jsonb, '{"en-us": "Activity affecting the synthesis of steroid hormones.", "pt-br": "Atividade que afeta a síntese de hormônios esteroides."}'::jsonb, 36, TRUE),
  (37, '3.2', 'photoreactivity', 31, '["78", "201"]'::jsonb, '{"en-us": "Photoreactivity", "pt-br": "Fotorreatividade"}'::jsonb, '{"en-us": "Capacity to undergo or initiate a chemical or biological reaction following exposure to light.", "pt-br": "Capacidade de sofrer ou iniciar uma reação química ou biológica após exposição à luz."}'::jsonb, 37, TRUE),
  (38, '4', 'ecotoxicological-effects', NULL, '["41", "42", "43", "44", "45", "46", "47", "48", "49", "50", "51", "52", "53", "54", "55", "56", "57"]'::jsonb, '{"en-us": "Ecotoxicological effects", "pt-br": "Efeitos ecotoxicológicos"}'::jsonb, '{"en-us": "Adverse effects of substances or other stressors on organisms, populations or ecological systems.", "pt-br": "Efeitos adversos de substâncias ou outros agentes estressores sobre organismos, populações ou sistemas ecológicos."}'::jsonb, 38, TRUE),
  (39, '4.1', 'aquatic-effects', 38, '["41", "42", "43", "44", "45", "46", "47"]'::jsonb, '{"en-us": "Aquatic effects", "pt-br": "Efeitos aquáticos"}'::jsonb, '{"en-us": "Adverse effects involving organisms or ecological processes in aquatic environments.", "pt-br": "Efeitos adversos que envolvem organismos ou processos ecológicos em ambientes aquáticos."}'::jsonb, 39, TRUE),
  (40, '4.1.1', 'aquatic-toxicity', 39, '["41", "42", "43", "44", "45", "46", "47"]'::jsonb, '{"en-us": "Aquatic toxicity", "pt-br": "Toxicidade aquática"}'::jsonb, '{"en-us": "Capacity to cause adverse effects in aquatic organisms.", "pt-br": "Capacidade de causar efeitos adversos em organismos aquáticos."}'::jsonb, 40, TRUE),
  (41, '4.1.2', 'fish-toxicity', 39, '["41", "42"]'::jsonb, '{"en-us": "Fish toxicity", "pt-br": "Toxicidade para peixes"}'::jsonb, '{"en-us": "Adverse effects on fish, including lethal, sublethal, developmental and reproductive effects.", "pt-br": "Efeitos adversos sobre peixes, incluindo efeitos letais, subletais, reprodutivos e sobre o desenvolvimento."}'::jsonb, 41, TRUE),
  (42, '4.1.3', 'aquatic-invertebrate-toxicity', 39, '["43", "44"]'::jsonb, '{"en-us": "Aquatic invertebrate toxicity", "pt-br": "Toxicidade para invertebrados aquáticos"}'::jsonb, '{"en-us": "Adverse effects on aquatic invertebrates, including acute and chronic effects.", "pt-br": "Efeitos adversos sobre invertebrados aquáticos, incluindo efeitos agudos e crônicos."}'::jsonb, 42, TRUE),
  (43, '4.1.4', 'aquatic-algae-plant-toxicity', 39, '["45", "46"]'::jsonb, '{"en-us": "Aquatic algae and plant toxicity", "pt-br": "Toxicidade para algas e plantas aquáticas"}'::jsonb, '{"en-us": "Adverse effects on aquatic algae, cyanobacteria or macrophytes.", "pt-br": "Efeitos adversos sobre algas, cianobactérias ou macrófitas aquáticas."}'::jsonb, 43, TRUE),
  (44, '4.2', 'terrestrial-effects', 38, '["48", "49", "50", "51", "52", "53", "54", "55", "56", "57"]'::jsonb, '{"en-us": "Terrestrial effects", "pt-br": "Efeitos terrestres"}'::jsonb, '{"en-us": "Adverse effects involving organisms or ecological processes in terrestrial environments.", "pt-br": "Efeitos adversos que envolvem organismos ou processos ecológicos em ambientes terrestres."}'::jsonb, 44, TRUE),
  (45, '4.3', 'sediment-organism-effects', 38, '[]'::jsonb, '{"en-us": "Sediment-organism effects", "pt-br": "Efeitos sobre organismos de sedimento"}'::jsonb, '{"en-us": "Adverse effects on organisms living in or closely associated with sediment.", "pt-br": "Efeitos adversos sobre organismos que vivem no sedimento ou estão estreitamente associados a ele."}'::jsonb, 45, TRUE),
  (46, '4.4', 'effects-on-biotic-systems-unspecified', 38, '["41", "42", "43", "44", "45", "46", "47", "48", "49", "50", "51", "52", "53", "54", "55", "56", "57"]'::jsonb, '{"en-us": "Effects on biotic systems, unspecified", "pt-br": "Efeitos em sistemas bióticos não especificados"}'::jsonb, '{"en-us": "Effects on biotic systems for which the affected organism or ecological compartment is not specified.", "pt-br": "Efeitos em sistemas bióticos para os quais o organismo afetado ou o compartimento ecológico não está especificado."}'::jsonb, 46, TRUE),
  (47, '5', 'product-safety-contaminant-targets', NULL, '[]'::jsonb, '{"en-us": "Product-safety and contaminant targets", "pt-br": "Alvos de segurança de produtos e contaminantes"}'::jsonb, '{"en-us": "Properties, contaminants or biological activities assessed to establish the safety or quality of a product.", "pt-br": "Propriedades, contaminantes ou atividades biológicas avaliadas para determinar a segurança ou a qualidade de um produto."}'::jsonb, 47, TRUE),
  (48, '5.1', 'pyrogenic-contamination', 47, '[]'::jsonb, '{"en-us": "Pyrogenic contamination", "pt-br": "Contaminação pirogênica"}'::jsonb, '{"en-us": "Presence or activity of fever-inducing substances in a product, especially a parenteral product.", "pt-br": "Presença ou atividade de substâncias indutoras de febre em um produto, especialmente em produtos parenterais."}'::jsonb, 48, TRUE),
  (49, '5.1.1', 'pyrogenicity', 48, '[]'::jsonb, '{"en-us": "Pyrogenicity", "pt-br": "Pirogenicidade"}'::jsonb, '{"en-us": "Capacity of a substance or product to induce a febrile response.", "pt-br": "Capacidade de uma substância ou produto de induzir uma resposta febril."}'::jsonb, 49, TRUE),
  (50, '5.1.2', 'bacterial-endotoxins', 48, '[]'::jsonb, '{"en-us": "Bacterial endotoxins", "pt-br": "Endotoxinas bacterianas"}'::jsonb, '{"en-us": "Lipopolysaccharides originating from the outer membrane of Gram-negative bacteria and assessed as pyrogenic contaminants.", "pt-br": "Lipopolissacarídeos provenientes da membrana externa de bactérias Gram-negativas e avaliados como contaminantes pirogênicos."}'::jsonb, 50, TRUE),
  (51, '5.1.3', 'non-endotoxin-pyrogens', 48, '[]'::jsonb, '{"en-us": "Non-endotoxin pyrogens", "pt-br": "Pirógenos não endotoxínicos"}'::jsonb, '{"en-us": "Pyrogenic substances other than bacterial endotoxins.", "pt-br": "Substâncias pirogênicas diferentes das endotoxinas bacterianas."}'::jsonb, 51, TRUE),
  (52, '6', 'diagnostic-targets', NULL, '[]'::jsonb, '{"en-us": "Diagnostic targets", "pt-br": "Alvos diagnósticos"}'::jsonb, '{"en-us": "Diseases, pathogens or biological conditions whose presence or identity is determined by a method.", "pt-br": "Doenças, patógenos ou condições biológicas cuja presença ou identidade é determinada por um método."}'::jsonb, 52, TRUE),
  (53, '6.1', 'infectious-disease-diagnosis', 52, '[]'::jsonb, '{"en-us": "Infectious-disease diagnosis", "pt-br": "Diagnóstico de doenças infecciosas"}'::jsonb, '{"en-us": "Detection or identification of an infectious disease or its causative agent.", "pt-br": "Detecção ou identificação de uma doença infecciosa ou de seu agente causador."}'::jsonb, 53, TRUE),
  (54, '6.1.1', 'rabies-diagnosis', 53, '[]'::jsonb, '{"en-us": "Rabies diagnosis", "pt-br": "Diagnóstico da raiva"}'::jsonb, '{"en-us": "Detection or confirmation of rabies virus infection in an animal.", "pt-br": "Detecção ou confirmação de infecção pelo vírus da raiva em um animal."}'::jsonb, 54, TRUE);

SELECT setval(
  'endpoints_id_seq',
  COALESCE((SELECT MAX(id) FROM endpoints), 1),
  true
);

ALTER TABLE endpoints
  ADD CONSTRAINT fk_endpoints_parent
  FOREIGN KEY (parent_id) REFERENCES endpoints(id) ON DELETE SET NULL;

ALTER TABLE route_endpoints
  ADD CONSTRAINT route_endpoints_endpoint_id_fkey
  FOREIGN KEY (endpoint_id) REFERENCES endpoints(id) ON DELETE CASCADE;

COMMENT ON COLUMN endpoints.external_oht_codes IS
  'OECD Harmonised Template codes as a JSON string array, e.g. ["58","66-1"].';

COMMIT;
