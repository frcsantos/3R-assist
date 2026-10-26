-- =============================================================================
-- Migration 114: Portuguese (pt-br) translations for documents.description
-- rows where pt-br was a copy of the English text (37 OECD documents), and
-- the pt-br regulatory_body of the two OECD regulations that still read "OECD".
-- Only rows whose pt-br is still identical to en-us are touched.
-- =============================================================================

BEGIN;

UPDATE documents d
SET description = jsonb_set(d.description, '{pt-br}', to_jsonb(v.pt))
FROM (VALUES
  (13, 'O método da classe tóxica aguda é um procedimento escalonado que usa o número mínimo de animais para classificar substâncias segundo sua toxicidade oral aguda, enquadrando-as em uma de várias classes de toxicidade com base em valores de corte fixos de DL50.'),
  (14, 'Coletânea de Diretrizes de Teste da OCDE para a avaliação de substâncias químicas, com foco em toxicidade aguda, imunotoxicidade e indução do citocromo P450.'),
  (15, 'Coletânea de diretrizes de teste reconhecidas internacionalmente para a avaliação de substâncias químicas, com foco em métodos in vitro para absorção percutânea, sensibilização cutânea, imunotoxicidade e indução do citocromo P450.'),
  (16, 'Diretriz que descreve o Ensaio do Linfonodo Local para sensibilização cutânea, incluindo padrões de desempenho e opções com redução do uso de animais, além de listar diversas outras Diretrizes de Teste da OCDE.'),
  (17, 'Coletânea de Diretrizes de Teste da OCDE para a avaliação de substâncias químicas, abrangendo desfechos como corrosão cutânea, sensibilização cutânea, imunotoxicidade e indução do citocromo P450.'),
  (18, 'Diretriz para a identificação de substâncias e misturas químicas corrosivas usando um modelo tridimensional de pele humana (epiderme humana reconstruída), sem o uso de animais vivos.'),
  (19, 'Este documento descreve um método in vitro para avaliar a fototoxicidade em células 3T3, comparando a viabilidade celular na presença e na ausência de exposição à luz.'),
  (20, 'Compilação de Diretrizes de Teste da OCDE para a avaliação de substâncias químicas, incluindo métodos in vitro para corrosão cutânea, sensibilização cutânea, imunotoxicidade e indução do citocromo P450.'),
  (21, 'Método de teste in vitro que utiliza córneas bovinas isoladas para identificar substâncias químicas que causam lesões oculares graves ou que não requerem classificação para irritação ocular ou lesões oculares graves segundo o GHS, servindo como alternativa ao teste em animais de laboratório.'),
  (22, 'Método de teste in vitro para a classificação de perigo ocular que utiliza olhos de galinha enucleados para identificar substâncias que causam lesões oculares graves ou não classificadas, eliminando a necessidade de animais de laboratório.'),
  (23, 'Diretriz de Teste da OCDE que descreve um procedimento in vitro com epiderme humana reconstruída (RhE) para a identificação de perigo de substâncias químicas irritantes (Categoria 2 do GHS da ONU), servindo como substituição independente ou parcial do teste in vivo.'),
  (24, 'Coletânea de Diretrizes de Teste da OCDE relacionadas à sensibilização cutânea, imunotoxicidade e indução do citocromo P450, descrevendo métodos para a avaliação de substâncias químicas e a avaliação regulatória.'),
  (25, 'Diretriz para a identificação de substâncias químicas com potencial de sensibilização cutânea por meio de uma modificação não radioativa do Ensaio do Linfonodo Local, baseada na medição do conteúdo de BrdU em células de linfonodos de camundongo.'),
  (26, 'Esta Diretriz de Teste apresenta métodos in chemico que abordam o evento-chave da Rota de Resultado Adverso relativo à ligação covalente a proteínas, para o desfecho de perigo de sensibilização cutânea.'),
  (27, 'Esta Diretriz de Teste apresenta cinco métodos de teste in vitro que abordam o evento-chave de ativação de queratinócitos na Rota de Resultado Adverso da sensibilização cutânea, utilizados para distinguir sensibilizantes de não sensibilizantes cutâneos.'),
  (28, 'Diretriz de teste da OCDE que aborda o desfecho de perigo à saúde humana de sensibilização cutânea, apresentando quatro métodos de teste in vitro que avaliam a ativação de células dendríticas na Rota de Resultado Adverso.'),
  (29, 'Ensaio in vitro que descreve o método de teste de vazamento de fluoresceína para identificar corrosivos oculares hidrossolúveis e irritantes graves, conforme definido pela Categoria 1 do GHS da ONU.'),
  (30, 'Coletânea de Diretrizes de Teste da OCDE para a avaliação de substâncias químicas, com foco em métodos de toxicologia e avaliação de segurança, incluindo mutagenicidade, sensibilização cutânea, imunotoxicidade e indução metabólica.'),
  (31, 'Coletânea de Diretrizes de Teste da OCDE para testes in vitro, abrangendo ensaios de mutação gênica, sensibilização cutânea, imunotoxicidade e indução do citocromo P450.'),
  (32, 'Teste de genotoxicidade in vitro para a detecção de micronúcleos originados de fragmentos cromossômicos acêntricos ou de cromossomos inteiros em células em interfase.'),
  (33, 'Diretriz de Teste da OCDE para um procedimento in vitro com construtos de tecido RhCE, que identifica substâncias químicas que não requerem classificação e rotulagem para irritação ocular ou lesões oculares graves segundo o GHS da ONU.'),
  (34, 'Coletânea de Diretrizes de Teste da OCDE para a avaliação de substâncias químicas, com foco em métodos in vitro para dano ocular, imunotoxicidade e indução do citocromo P450.'),
  (35, 'Coletânea de diretrizes de teste baseadas em desempenho e de ensaios para testes químicos in vitro, incluindo a transativação do receptor de estrogênio e as rotas de sensibilização cutânea.'),
  (36, 'Este documento descreve uma Diretriz de Teste Baseada em Desempenho para ensaios in vitro com receptor humano recombinante, destinados a detectar substâncias com afinidade de ligação ao receptor de estrogênio, para fins de triagem e priorização.'),
  (37, 'O documento apresenta uma Diretriz de Teste da OCDE para uma triagem in vitro dos efeitos de substâncias químicas sobre a esteroidogênese, usando a linhagem celular humana H295R para medir a produção de 17ß-estradiol e testosterona.'),
  (38, 'Esta diretriz descreve ensaios ARTA in vitro com linhagens celulares estavelmente transfectadas (AR-EcoScreen, AR-CALUX, 22Rv1/MMTV_GR-KO) para identificar agonistas e antagonistas do receptor de andrógeno.'),
  (39, 'Coletânea de Diretrizes de Teste da OCDE para a avaliação de substâncias químicas, com foco em genotoxicidade e nas rotas de sensibilização cutânea.'),
  (40, 'Coletânea de Diretrizes de Teste da OCDE para a avaliação de substâncias químicas, abrangendo testes de mutação gênica in vitro e ensaios de sensibilização cutânea.'),
  (41, 'Diretriz de Teste da OCDE que descreve o Teste de Irritação Ocular Vitrigel (EIT), um método in vitro que usa modelos de epitélio corneano humano para identificar substâncias químicas que não requerem classificação para irritação ocular ou lesões oculares graves, com base em alterações na função de barreira.'),
  (42, 'A Diretriz de Teste 496 da OCDE descreve um método de teste bioquímico in vitro que usa uma matriz macromolecular para identificar substâncias químicas que induzem lesões oculares graves ou que não requerem classificação para irritação ocular ou lesões oculares graves.'),
  (43, 'Coletânea de Diretrizes de Teste da OCDE para a avaliação de substâncias químicas, incluindo métodos para avaliar fototoxicidade, imunotoxicidade e indução do citocromo P450.'),
  (44, 'Diretriz da OCDE para a avaliação de substâncias químicas que descreve um teste de toxicidade de curto prazo em estágios de embrião e alevino de peixe, para determinar efeitos letais e subletais de substâncias dissolvidas na água.'),
  (45, 'Coletânea de Diretrizes de Teste da OCDE para a avaliação de substâncias químicas, incluindo protocolos específicos para peixes, algas, minhocas e mamangavas (Bombus).'),
  (46, 'Descreve o uso de hepatócitos criopreservados de truta-arco-íris como sistema metabolizante para determinar o clearance intrínseco in vitro de uma substância química de teste.'),
  (47, 'Esta diretriz de teste descreve o uso da fração subcelular S9 de fígado de truta-arco-íris como sistema metabolizante para determinar o clearance intrínseco in vitro de uma substância química de teste, com o objetivo de melhorar as previsões in silico de bioacumulação em peixes.'),
  (48, 'Diretriz de Teste da OCDE para a triagem dos efeitos de substâncias químicas sobre o desempenho reprodutivo de machos e fêmeas, atualizada para incluir desfechos de desreguladores endócrinos, como a distância anogenital, a retenção de mamilos e o exame da tireoide em ratos.'),
  (49, 'Compilação de Diretrizes de Teste da OCDE para a avaliação de substâncias químicas, incluindo protocolos para triagem de toxicidade, imunotoxicidade e indução do citocromo P450.')
) AS v(id, pt)
WHERE d.id = v.id
  AND d.description->>'pt-br' = d.description->>'en-us';

UPDATE regulations
SET regulatory_body = jsonb_set(
      regulatory_body, '{pt-br}',
      to_jsonb('Organização para a Cooperação e Desenvolvimento Econômico (OCDE)'::text))
WHERE id IN (47, 103)
  AND regulatory_body->>'pt-br' = 'OECD';

COMMIT;
