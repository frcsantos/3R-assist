-- =============================================================================
-- Migration 076: method descriptions from curator feedback (docs/feedback_checklist.md)
-- and replacement rationale for GD 129.
-- Titles are unchanged. en-us texts follow the pt-br wording requested.
-- text_for_embedding / embedding_json are not regenerated here.
-- =============================================================================

BEGIN;

-- Full replacements -----------------------------------------------------------
UPDATE methods m
SET description = jsonb_build_object('en-us', v.en, 'pt-br', v.pt)
FROM (VALUES
  (3,  'In vitro method that uses a three-dimensional reconstructed human epidermis with a functional stratum corneum to identify corrosive and non-corrosive substances and mixtures based on the reduction in cell viability after defined exposure periods.',
       'Método in vitro que utiliza epiderme humana reconstruída tridimensional, com estrato córneo funcional, para identificar substâncias e misturas corrosivas e não corrosivas com base na redução da viabilidade celular após períodos definidos de exposição.'),
  (5,  'An in vitro membrane barrier test method that uses an artificial membrane designed to respond to corrosive chemicals in a manner similar to skin to identify corrosive chemicals.',
       'Um método de teste de barreira de membrana in vitro que utiliza uma membrana artificial projetada para responder a produtos químicos corrosivos de maneira semelhante à pele para identificar produtos químicos corrosivos.'),
  (22, 'In vitro basal cytotoxicity assay based on neutral red uptake (NRU), using BALB/c 3T3 cells or normal human keratinocytes (NHK). The IC50 obtained is used to estimate an LD50 and to support the selection of the starting dose in in vivo acute oral toxicity tests, with the potential to reduce the number of animals used.',
       'Ensaio de citotoxicidade basal in vitro baseado na captação de vermelho neutro (NRU), utilizando células BALB/c 3T3 ou queratinócitos humanos normais (NHK). O IC50 obtido é utilizado para estimar uma LD50 e auxiliar na seleção da dose inicial de testes de toxicidade aguda oral in vivo, com potencial de reduzir o número de animais utilizados.'),
  (30, 'Laboratory diagnostic technique used to detect rabies virus antigens in brain tissue impressions or smears, using fluorescein-conjugated anti-rabies antibodies.',
       'Técnica de diagnóstico laboratorial utilizada para detectar antígenos do vírus da raiva em impressões ou esfregaços de tecido cerebral, por meio de anticorpos anti-rábicos conjugados à fluoresceína.'),
  (41, 'Performance-based guideline for in vitro assays with stably transfected cell lines, used to identify substances with agonist or antagonist activity on estrogen receptors through reporter gene transactivation.',
       'Diretriz baseada em desempenho para ensaios in vitro com linhagens celulares estavelmente transfectadas, utilizados para identificar substâncias com atividade agonista ou antagonista sobre receptores de estrogênio por meio da transativação de gene repórter.')
) AS v(id, en, pt)
WHERE m.id = v.id;

-- Targeted edits -----------------------------------------------------------
UPDATE methods SET description = jsonb_build_object(
  'en-us', replace(description->>'en-us', 'An in vitro test method', 'An ex vivo test method'),
  'pt-br', replace(description->>'pt-br', 'método de teste in vitro', 'método de teste ex vivo'))
WHERE id IN (6, 7);

UPDATE methods SET description = jsonb_set(description, '{pt-br}',
  to_jsonb(replace(description->>'pt-br', 'evento iniciador molecular', 'evento molecular inicial')))
WHERE id = 10;

UPDATE methods SET description = jsonb_build_object(
  'en-us', replace(replace(description->>'en-us', 'photo-cytotoxicity', 'phototoxicity'), 'Balb/c 3T3 cells', 'Balb/c 3T3 cells (murine fibroblast cell line)'),
  'pt-br', replace(replace(description->>'pt-br', 'foto-citotoxicidade', 'fototoxicidade'), 'Balb/c 3T3 expostas', 'Balb/c 3T3 (linhagem de fibroblastos murinos) expostas'))
WHERE id = 16;

UPDATE methods SET description = jsonb_build_object(
  'en-us', replace(description->>'en-us', 'Intended to replace mouse inoculation tests for virus isolation.', 'Can replace the mouse inoculation test (MIT) for animal rabies diagnosis.'),
  'pt-br', replace(description->>'pt-br', 'Destina-se a substituir testes de inoculação em camundongos para isolamento viral.', 'Pode substituir o teste de inoculação em camundongos (Mouse inoculation Test - MIT) para diagnóstico da raiva animal.'))
WHERE id = 35;

-- GD 129: also usable as replacement, depending on the regulator ----------------
UPDATE methods SET replacement_rationale = jsonb_build_object(
  'en-us', 'Depending on the regulatory authority, the in vitro basal cytotoxicity result may also be used as a replacement for in vivo acute oral toxicity testing.',
  'pt-br', 'Dependendo da autoridade regulatória, o resultado de citotoxicidade basal in vitro também pode ser usado como método de substituição ao teste de toxicidade oral aguda in vivo.')
WHERE id = 22 AND replacement_rationale IS NULL;

COMMIT;
