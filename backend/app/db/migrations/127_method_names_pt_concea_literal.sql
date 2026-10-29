-- =============================================================================
-- Migration 127: pt-br method names set to the CONCEA resolution wording,
-- prefixed with the guideline code ("TG nnn - "), from the "Nome proposto"
-- column of docs/curadoria_decisoes.xlsx (sheet 5_Nomes). Methods without a TG
-- (MAT, LAL, rFC, rabies) carry the resolution wording without a prefix.
-- Only name->'pt-br' changes; en-us is untouched.
-- =============================================================================

BEGIN;

UPDATE methods m
SET name = jsonb_set(m.name, '{pt-br}', to_jsonb(v.pt))
FROM (VALUES
  (1, 'TG 439 - Teste de irritação Cutânea in vitro'),
  (3, 'TG 431 - Corrosão dérmica in vitro: Teste da Epiderme Humana Reconstituída (RHE)'),
  (4, 'TG 430 - Corrosão dérmica in vitro: Teste de Resistência Elétrica Transcutânea (TER)'),
  (5, 'TG 435 - Teste de Barreira de Membrana in vitro'),
  (6, 'TG 437 - Teste de Permeabilidade e Opacidade de Córnea Bovina'),
  (7, 'TG 438 - Teste de Olho Isolado de Galinha'),
  (8, 'TG 460 - Teste de Permeação de Fluoresceína'),
  (9, 'TG 492 - Epitélio corneal humano reconstruído (RhCE)'),
  (10, 'TG 442C - Sensibilização cutânea in chemico'),
  (11, 'TG 442D - Sensibilização cutânea in vitro: Evento-Chave de Ativação de Queratinócitos'),
  (12, 'TG 442E - Sensibilização cutânea in vitro: ensaios de sensibilização cutânea in vitro abordando o evento chave na ativação de células dendríticas no Caminho da Resposta Adversa (AOP) para sensibilização cutânea'),
  (13, 'TG 429 - Sensibilização Cutânea: Ensaio do Linfonodo Local'),
  (14, 'TG 442A - Versões não radioativas do Ensaio do Linfonodo Local (ATP)'),
  (15, 'TG 442B - Versões não radioativas do Ensaio do Linfonodo Local (BrdU-ELISA or -FCM)'),
  (16, 'TG 432 - Teste de Fototoxicidade in vitro 3T3 NRU'),
  (17, 'TG 471 - Teste de mutação bacteriana reversa'),
  (18, 'TG 476 - Testes in vitro de mutação gênica de células de mamífero usando os gens Hprt and xprt'),
  (19, 'TG 487 - Teste do Micronúcleo em Célula de Mamífero in vitro'),
  (20, 'Teste de Ativação de Monócitos (MAT)'),
  (21, 'TG 428 - Absorção Cutânea método in vitro'),
  (22, 'TG 129 - estimativa da dose inicial para teste de toxicidade aguda oral sistêmica'),
  (23, 'TG 420 - Toxicidade Aguda Oral – Procedimento de Doses Fixas'),
  (24, 'TG 423 - Toxicidade Aguda Oral – Classe Tóxica Aguda'),
  (25, 'TG 425 - Toxicidade Aguda Oral – procedimento "Up and Down"'),
  (30, 'Técnica de Imunofluorescência Direta (Direct Fluorescent Antibody Test) - DFA Test'),
  (33, 'Teste Rápido de Imuno-histoquímica Direta (Direct Rapid Immunohistochemistry Test) - dRIT'),
  (34, 'Isolamento viral em cultivo celular (Rabies Tissue Culture Infection Test - RTCIT)'),
  (35, 'Técnicas moleculares baseadas em Reação de Transcriptase Reversa, seguida de Reação em Cadeia da Polimerase quantitativa (RT-qPCR) ou convencional (RT-PCR)'),
  (36, 'TG 421 - Teste de triagem para toxicidade reprodutiva e do desenvolvimento'),
  (37, 'TG 422 - Estudo de toxicidade repetida combinado com teste de toxicidade reprodutiva'),
  (38, 'Teste de Endotoxina Bacteriana (LAL) (Farmacopeia Brasileira)'),
  (39, 'TG 492B - Epitélio semelhante à córnea humano reconstruído (Reconstructed Human Cornea-like Epithelium (RhCE) Test Method for Eye Hazard Identification)'),
  (40, 'TG 491 - Teste in vitro de curta duração para danos oculares'),
  (41, 'TG 455 - Teste baseado na performance para ensaios in vitro de transativação transfectada estável para detectar agonistas e antagonistas de receptor estrogênico'),
  (42, 'TG 493 - Teste baseado na performance para ensaios in vitro de receptor estrogênico humano recombinante (hrER) para detectar substâncias químicas com afinidade de ligação ER'),
  (43, 'TG 456 - Ensaio de Esteroidogênese H295R'),
  (44, 'TG 458 - Ensaio de ativação transcripcional de receptores androgênicos humanos transfectados para detecção de atividade agonista e antagonista de substâncias químicas'),
  (45, 'TG 473 - Teste in vitro de aberração cromossômica de mamíferos'),
  (46, 'TG 490 - Testes in vitro de mutação gênica em células de mamífero usando gen Timidinaquinase'),
  (47, 'TG 494 - Vitrigel - Teste de irritação ocular para identificação de substâncias químicas que não requerem classificação e rotulagem para irritação ocular ou sério dano ocular'),
  (49, 'TG 496 - Teste macromolecular in vitro para identificação de substâncias químicas que induzem dano ocular severo e substâncias químicas que não requerem classificação para irritação ocular ou dano ocular severo'),
  (50, 'TG 495 - Ensaio de fotorreatividade por Ros (Espécies oxigênio reativas)'),
  (51, 'TG 212 - Peixe, teste de toxicidade a curto prazo em estágios embrionários e recém nascidos'),
  (53, 'TG 236 - Toxicidade aguda em embrião de peixe (FET)'),
  (54, 'TG 319A - Determinação do "clearance" intrínseco "in vitro" usando hepatócitos criopreservados de Truta Arco-Íris (RT-HEP)'),
  (55, 'TG 319B - Determinação do "clearance" intrínseco "in vitro" usando fração sub-celular S-9 de Truta Arco-Íris (RT-S9)'),
  (56, 'Fator C recombinante (rFC) para detecção de endotoxinas bacterianas')
) AS v(id, pt)
WHERE m.id = v.id;

COMMIT;
