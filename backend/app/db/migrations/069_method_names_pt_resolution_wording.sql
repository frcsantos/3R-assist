-- =============================================================================
-- Migration 069: align pt-br method names with the wording of the CONCEA
-- resolutions (regulatory_quote) where the two are equivalent, and
-- disambiguate TG 442D / TG 442E, which became identical after 068.
--
-- Capitalisation: major words capitalised, prepositions/articles/conjunctions
-- lower case; acronyms kept when one exists.
-- TG 442D / 442E subtitles taken from the OECD PDFs (Key Event on
-- keratinocyte activation / dendritic cell activation).
-- =============================================================================

BEGIN;

UPDATE methods m
SET name = jsonb_set(m.name, '{pt-br}', to_jsonb(v.pt))
FROM (VALUES
  (6,  'Teste de Permeabilidade e Opacidade de Córnea Bovina (BCOP)'),
  (7,  'Teste de Olho Isolado de Galinha'),
  (17, 'Teste de Mutação Bacteriana Reversa'),
  (19, 'Teste do Micronúcleo em Célula de Mamífero In Vitro'),
  (21, 'Absorção Cutânea: Método In Vitro'),
  (23, 'Toxicidade Aguda Oral – Procedimento de Doses Fixas'),
  (24, 'Toxicidade Aguda Oral – Classe Tóxica Aguda'),
  (25, 'Toxicidade Aguda Oral – Procedimento Up and Down'),
  (36, 'Teste de Triagem para Toxicidade Reprodutiva e do Desenvolvimento'),
  (45, 'Teste In Vitro de Aberração Cromossômica de Mamíferos'),
  (53, 'Toxicidade Aguda em Embrião de Peixe (FET)'),
  (18, 'Testes In Vitro de Mutação Gênica de Células de Mamífero Usando os Genes Hprt e xprt'),
  (46, 'Testes In Vitro de Mutação Gênica em Células de Mamífero Usando o Gene da Timidina Quinase'),
  (38, 'Teste de Endotoxina Bacteriana (LAL)'),
  (11, 'Sensibilização Cutânea In Vitro: Evento-Chave de Ativação de Queratinócitos'),
  (12, 'Sensibilização Cutânea In Vitro: Evento-Chave de Ativação de Células Dendríticas')
) AS v(id, pt)
WHERE m.id = v.id;

UPDATE methods
SET name = jsonb_set(name, '{en-us}', to_jsonb('In Vitro Skin Sensitisation: Key Event on Keratinocyte Activation'::text))
WHERE id = 11;

UPDATE methods
SET name = jsonb_set(name, '{en-us}', to_jsonb('In Vitro Skin Sensitisation: Key Event on Dendritic Cell Activation'::text))
WHERE id = 12;

COMMIT;
