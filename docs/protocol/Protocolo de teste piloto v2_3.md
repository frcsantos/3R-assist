# Protocolo Piloto de Calibração e Validação para a Correspondência entre Experimentos com Animais e Métodos Alternativos

**Versão:** 2.3-piloto · **Data:** 06/11/2026  
**Sistema:** Assist3R

## Sumário

1. [Objetivos e o que se herda do protocolo completo](#1-objetivos-e-o-que-se-herda-do-protocolo-completo)  
2. [Tamanhos e carga de trabalho](#2-tamanhos-e-carga-de-trabalho)  
3. [Como encontrar os artigos](#3-como-encontrar-os-artigos)  
4. [Extração da consulta](#4-extração-da-consulta)  
5. [Rotulagem por especialistas e pelo juiz LLM](#5-rotulagem-por-especialistas-e-pelo-juiz-llm)  
6. [Pools do Basket 2](#6-pools-do-basket-2)  
7. [Estabilidade](#7-estabilidade)  
8. [Métricas reportadas](#8-métricas-reportadas)  
9. [Sinais de parada e decisão](#9-sinais-de-parada-e-decisão)  
10. [Saídas para dimensionar o estudo completo](#10-saídas-para-dimensionar-o-estudo-completo)  
11. [Cronograma sugerido](#11-cronograma-sugerido)  
12. [Referências](#12-referências)

## 1\. Objetivos

### 1.1 Objetivos

1. **Viabilidade:** verificar se é possível encontrar casos, extrair consultas, rotular pares e rodar o pipeline de ponta a ponta com os recursos disponíveis.  
2. **Estimação de parâmetros:** medir a prevalência dos graus, a taxa de U, o tamanho do fluxo de endossos fortes do juiz LLM, o tempo médio por avaliação especialista e a taxa de adjudicação.  
3. **Detecção de falhas grosseiras:** rubrica pouco confiável, extrator que inventa restrições, juiz que endossa com frequência candidatos inadequados, afirmações inseguras exibidas ao usuário.

## 2\. Tamanhos e carga de trabalho

**Tabela 1 — Casos do piloto**

| Estrato | Casos | Seleção (detalhes no §3) | B1 | B2 |
| :---- | :---- | :---- | :---- | :---- |
| A: direcionado a métodos | 20 | 20 dos 47 métodos, sorteados com estratificação por família de métodos; 1 procedimento por método | Sim | Não |
| B: proxy de publicações | 20 | Amostra aleatória de artigos com animais de um quadro PubMed definido | Sim | Sim |
| C: difícil/negativo | 15 | Quase acertos, substituição parcial, ausência de correspondência, subespecificação | Sim | Sim |
| D: semeado pela literatura | 15 | Pistas de alternativas encontradas com 3Ranker, SMAFIRA e busca manual, associadas a procedimentos com animais | Não | Sim |
| **Total** | **70** |  | **55 consultas** | **50 consultas** |

Com 55 consultas, B1 gera 55 × 47 \= 2.585 pares, todos julgados pelo LLM. B2 gera cerca de 20 artigos por consulta após a deduplicação (§6), ou seja, \~1.000 pares julgados pelo LLM.

**Tabela 2 — Carga especialista estimada**

| Tarefa | Por basket | Total (B1 \+ B2) | Tempo estimado por item | Horas |
| :---- | :---- | :---- | :---- | :---- |
| Pares com dupla codificação (§5.2) | 50 pares × 2 avaliadores | 200 avaliações | \~5 min | \~17 h |
| Auditoria de endossos fortes (§5.3) | 30 pares × 1 avaliador | 60 avaliações | \~5 min | \~5 h |
| Adjudicações | \~15% dos pares | \~25 | \~10 min | \~4 h |
| Extração de referência (§4) | — | 30 casos \+ 10 revisados por um 2º especialista | \~15 min | \~10 h |
| **Total** |  | **\~315 tarefas** |  | **\~35 h** |

Os tempos por item são suposições de planejamento; medi-los é um dos objetivos do piloto (§10). Com dois especialistas, isso equivale a cerca de 17–18 h por pessoa.

**Versão reduzida.** Se o orçamento não comportar os números acima, reduza os pares com dupla codificação para **30 por basket** (o IC 95% do κ se alarga de cerca de ±0,08 para ±0,12) ou rode o piloto **só em B1**, eliminando o estrato D e cortando cerca de metade da carga especialista.

## 3\. Como encontrar os artigos

Cada estrato exige um tipo diferente de artigo. Os estratos A, B e C precisam de **artigos que descrevem procedimentos com animais**: são a fonte das consultas. O estrato D precisa de **artigos que descrevem abordagens sem animais**: são as pistas que o Basket 2 deveria encontrar, depois associadas a um procedimento com animais.

O 3Ranker serve bem para o segundo tipo, mas não para o primeiro (§3.1).

### 3.1 Ferramentas e para que cada uma serve

**Tabela 3 — Ferramentas de busca**

| Ferramenta | O que faz | Uso no piloto | Limitações |
| :---- | :---- | :---- | :---- |
| **3Ranker** (open3r.org) | Pontua resumos do MEDLINE quanto à relação com os 3Rs, a partir de um termo de busca; exibe os 200 resumos de maior escore. Tem também uma coleção de resumos curados por especialistas como relacionados aos 3Rs \[R1, R2\] | Fonte principal de pistas do estrato D; fonte opcional de candidatos para os pools de B2 | Só mostra o topo (sem faixas baixas de escore); classificador treinado inicialmente em poucos domínios (pele); detecta artigos *sobre* 3Rs, não adequação a um procedimento específico; não há exportação nem API documentadas |
| **SMAFIRA** (smafira.bf3r.de) | Busca no PubMed e classifica os resumos por modelo experimental: *in vivo*, órgãos, células primárias, linhagens imortalizadas, invertebrados, humanos, *in silico*, outros \[R3\] | Confirmar que um artigo usa animais (*in vivo*) para A, B e C; encontrar artigos sem animais (rótulos não *in vivo*) para D | Classificação automática: confirme manualmente; rótulos multiclasse podem coexistir |
| **PubMed \+ filtro de experimentação animal** | Busca bibliográfica com filtro validado para estudos com animais \[R4\] e acesso programático via E-utilities | Quadro amostral do estrato B; busca por desfecho no estrato A | Exige montar e congelar a string de busca |
| **Bases curadas de métodos** (EURL ECVAM, TSAR, NC3Rs, Norecopa 3R Guide, RE-Place) \[R5\] | Catálogos e revisões de métodos alternativos | Confirmar o uso pretendido e as restrições dos métodos de B1; casos difíceis para C | Não fornecem procedimentos com animais |

### 3.2 Estrato A — procedimentos com animais para os métodos de B1

1. **Sorteio dos métodos.** Agrupe os 47 métodos de B1 por família (por exemplo: modelos de pele, modelos hepáticos, ensaios de genotoxicidade, *in silico*) e sorteie 20, proporcionalmente às famílias, com semente registrada.  
2. **Busca.** Para cada método sorteado, identifique o desfecho e o propósito que ele atende (pelas especificações em B1). Busque no PubMed estudos com animais que medem esse desfecho, combinando os termos do desfecho com o filtro de experimentação animal \[R4\].  
3. **Seleção.** Dentre os resultados elegíveis (ver critérios no §3.7), sorteie um artigo. Confirme no SMAFIRA ou manualmente que o artigo é *in vivo*.  
4. **Ocultação da semente.** O método que originou a busca vai para `seed_ids_hidden_from_judges`. Não é um positivo presumido: os especialistas podem atribuir qualquer grau (protocolo completo, §2.2).

**Não use o 3Ranker no estrato A.** Ele ranqueia artigos sobre alternativas, e o estrato A precisa de artigos com animais.

### 3.3 Estrato B — amostra aleatória de artigos com animais

Este estrato é um **proxy fraco** (protocolo completo, §2.3, tipo 3): mede uma população de publicações, não o uso real.

1. **Defina e congele o quadro.** Uma string de busca no PubMed com: filtro de experimentação animal \[R4\]; período (por exemplo, 2020–2025); idioma; tipo de publicação (artigos originais); e, opcionalmente, áreas temáticas alinhadas ao escopo do Assist3R.  
2. **Baixe os PMIDs** com o E-utilities (`esearch`) e registre a data, a string exata e o total de resultados.  
3. **Sorteie** 40 PMIDs com semente registrada (o dobro do necessário, para cobrir exclusões).  
4. **Triagem na ordem do sorteio.** Aplique os critérios de elegibilidade (§3.7) até completar 20 casos. Registre cada exclusão e seu motivo.

### 3.4 Estrato C — casos difíceis e negativos

Construa os 15 casos a partir de três fontes:

- **Quase acertos** (cerca de 6): artigos com animais cujo desfecho é *parecido*, mas não idêntico, ao de um método de B1 (por exemplo, mesma via biológica, tecido diferente). Use as buscas do estrato A.  
- **Sem correspondência esperada** (cerca de 5): procedimentos com animais de áreas sem métodos em B1, ou que exigem complexidade sistêmica não modelada (por exemplo, comportamento, interações entre órgãos). Use o quadro do estrato B.  
- **Subespecificados** (cerca de 4): artigos com seções de métodos incompletas, em que a resposta correta é pedir esclarecimento.

Registre o tipo de dificuldade pretendido, mas lembre que ele **não** é o rótulo: os especialistas rotulam de forma independente.

### 3.5 Estrato D — pistas da literatura emergente (onde entra o 3Ranker)

Cada caso do estrato D é um **par**: um artigo com uma abordagem sem animais (a pista) e um procedimento com animais ao qual ela poderia se aplicar (a consulta).

1. **Defina 5 temas** de desfecho (por exemplo: irritação cutânea, hepatotoxicidade, neurotoxicidade, inflamação pulmonar, cardiotoxicidade), cobrindo as famílias de métodos do Assist3R.  
2. **Busque pistas por três vias independentes**, para cada tema:  
   - **3Ranker:** busque o termo do tema e registre os 200 resultados exibidos com escore e posição. Sorteie candidatos entre eles, não só no topo.  
   - **SMAFIRA:** busque o mesmo tema e filtre por rótulos sem animais (órgãos, células primárias, linhagens imortalizadas, *in silico*).  
   - **Busca manual:** PubMed com termos de métodos (*organoid*, *organ-on-chip*, *in silico*, *3D model* etc.) mais o tema, e rastreamento de citações a partir de revisões recentes.  
3. **Monte a lista de candidatos** de cada tema e sorteie 3 pistas por tema (15 no total), com **no máximo 2 por tema vindas da mesma via** — ou seja, no máximo cerca de metade do estrato D vem do 3Ranker.  
4. **Associe um procedimento com animais.** Para cada pista, busque no PubMed (com filtro de experimentação animal \[R4\]) um estudo com animais que mede o mesmo desfecho. Esse estudo fornece o texto da consulta.  
5. **Registre a origem** em `discovery_source` (`3ranker`, `smafira`, `manual_pubmed`, `citation_tracking`) e o escore ou posição original, quando houver.

**Riscos de usar o 3Ranker e como mitigá-los:**

- **Viés de origem.** Se o estrato D vier só do 3Ranker, o benchmark mede o quanto o Basket 2 concorda com o 3Ranker. Daí o limite de 2 por tema e a análise por `discovery_source` (§8).  
- **Circularidade.** Antes de começar, confirme se o 3Ranker, ou um classificador derivado dele, é componente do Basket 2 do Assist3R. Se for, as pistas vindas do 3Ranker **não** podem medir a recuperação do Basket 2: use-as apenas para testar a rotulagem, e reporte a recuperação só com pistas das outras vias.  
- **Relevância genérica ≠ adequação.** Um escore alto no 3Ranker indica relação com os 3Rs, não que o artigo seja uma boa pista para o procedimento associado. O grau de B2 é sempre atribuído pelos especialistas ou pelo juiz.  
- **Cobertura de domínios.** O classificador foi desenvolvido inicialmente com artigos de pele. Em temas distantes, espere menos pistas úteis e registre isso como dado do piloto.

### 3.6 Registro obrigatório por caso

Além dos campos do protocolo completo (§3.1 e §13.1), registre: `stratum`, `discovery_source`, `search_string`, `search_date`, `rng_seed`, `draw_position`, `screening_decision`, `exclusion_reason` e, para D, `lead_article_id` e `three_ranker_score_or_rank` quando aplicável.

### 3.7 Critérios de elegibilidade dos artigos-fonte (estratos A, B, C e D)

Inclua artigos que: (1) descrevem pelo menos um procedimento com animais com objetivo e desfecho identificáveis; (2) têm seção de métodos acessível (acesso aberto ou institucional); (3) estão em inglês ou português.

Exclua: revisões, editoriais, protocolos sem resultados, estudos exclusivamente em humanos, estudos veterinários clínicos sem procedimento experimental, e duplicatas de grupo de origem (mesmo laboratório e projeto de um caso já incluído).

## 4\. Extração da consulta

Versão reduzida do protocolo completo, §3.2:

1. **30 casos**, cerca de 7–8 por estrato, incluindo pelo menos 4 casos subespecificados do estrato C.  
2. Um especialista constrói a extração de referência a partir do **texto original**, sem ver a extração do motor. Um segundo especialista revisa 10 desses casos de forma independente; as divergências são adjudicadas.  
3. Compare com a extração automática: campos críticos preservados, restrições inventadas, omissões relevantes, confusão entre desconhecido e inferido.  
4. Rode o caminho oráculo (extração de referência → motor) nesses 30 casos e compare o top-5 (B1) e o top-10 (B2) com o caminho de produção.

Zero erros críticos em 30 casos dá um limite superior unilateral de 95% de 9,5%. É um número **descritivo**: o piloto não qualifica o extrator.

## 5\. Rotulagem por especialistas e pelo juiz LLM

### 5.1 Juiz LLM

O juiz rotula, de forma cega (protocolo completo, §6.1): os 47 métodos de cada consulta de B1 e todos os artigos de cada pool de B2. Esses rótulos são **provisórios** e servem para três coisas: as métricas provisórias (§8), o sorteio da amostra estratificada por escore e a identificação do fluxo de endossos fortes.

### 5.2 Pares com dupla codificação (50 por basket)

1. Congele os escores do motor para todos os pares.  
2. Divida os pares em **5 faixas de escore** (quintis do escore normalizado) e sorteie **10 pares por faixa**, com no máximo um par por grupo de origem sempre que possível.  
3. Dois especialistas rotulam cada par de forma independente e cega: não veem escore, ranque, semente, rótulo do LLM nem a avaliação do outro.  
4. Divergências de 2 ou mais graus, de escopo (`complete` versus `partial`) e de critério eliminatório são adjudicadas por um terceiro especialista ou por consenso documentado.

Esses 50 pares cumprem três funções: estimar a confiabilidade entre especialistas, servir de referência para avaliar o juiz LLM e funcionar como auditoria ampla (a seleção não depende do rótulo do LLM). **Não** são uma amostra representativa: as estimativas de erro valem para a amostra estratificada, não para a população de pares.

### 5.3 Auditoria de endossos fortes (30 por basket)

1. Liste todos os pares com grau 3 atribuído pelo LLM (em B2, pistas fortes). Esse é o fluxo de endossos fortes.  
2. Ordene-os aleatoriamente com semente registrada e escolha os primeiros 30 de grupos de origem distintos, excluindo os pares já sorteados no §5.2.  
3. Um especialista rotula cada par às cegas. Os pares que ele classificar como grau 0 ou 1, ou com critério eliminatório reprovado, passam por um segundo especialista.  
4. Conte os **endossos inseguros** confirmados (definição no protocolo completo, §6.2).  
5. **Registre o tamanho total do fluxo** e o número de grupos de origem distintos nele: esse número define se o estudo completo é viável (§10).

Se o fluxo tiver menos de 30 grupos distintos, audite todos e registre a insuficiência.

## 6\. Pools do Basket 2

Para cada uma das 50 consultas de B2:

1. top-10 do Basket 2 em produção;  
2. top-10 de uma busca BM25/lexical independente sobre o mesmo snapshot do índice;  
3. **opcional:** top-10 do 3Ranker para os termos da consulta, se a extração manual for viável (§3.1). Não use o 3Ranker no pool se ele for componente do Basket 2;  
4. a pista do estrato D, quando houver;  
5. deduplicação, resultando em cerca de 15–25 artigos por consulta.

Registre se a pista do estrato D estava no índice (`not_in_index`), foi recuperada e em que posição (protocolo completo, §7.1). Artigos fora do pool são **não julgados**, não irrelevantes.

## 7\. Estabilidade

Em **10 consultas por basket**, execute o motor **3 vezes** com entrada, snapshot e configuração idênticos, na condição com candidatos travados. Reporte a identidade do top-1, o Jaccard no top-3 (B1) e no top-10 (B2) e qualquer mudança nas afirmações exibidas. Sem envolvimento de especialistas.

## 8\. Métricas reportadas

Todas as métricas são exploratórias, com IC 95% por bootstrap de grupos de origem (2.000 reamostragens, semente registrada) e com `n` explícito.

**Tabela 4 — Métricas do piloto**

| Bloco | Métricas |
| :---- | :---- |
| Extração | Erros críticos (contagem e limite exato); concordância por campo; diferença no top-k entre os caminhos oráculo e de produção |
| Especialista × especialista | κ ponderado quadrático com IC; concordância exata; matriz de confusão; taxa de U; divergências 0↔3 |
| LLM × especialista | κ ponderado com IC; matriz de confusão; erros 0↔3; endossos inseguros (contagem/30 e limite exato); sensibilidade para o grau 3 (descritiva) |
| Ranqueamento (provisório) | B1: nDCG@5 e Success@3 com rótulos do LLM. B2: nDCG@10 com rótulos do LLM; posição da pista do estrato D |
| Origem das pistas (B2) | Recuperação e posição das pistas do estrato D **por `discovery_source`** |
| Estabilidade | Identidade no top-1; Jaccard; mudanças nas afirmações |
| Afirmações exibidas | Contagem de afirmações sem respaldo de substituição completa (B1) ou validada (B2) |

**Nunca** apresente o nDCG provisório como desempenho validado, nem some resultados de estratos diferentes numa métrica global.

## 9\. Sinais de parada e decisão

**Tabela 5 — Sinais e consequências**

| Sinal | Regra | Consequência |
| :---- | :---- | :---- |
| Afirmação exibida insegura | ≥ 1 afirmação sem respaldo de substituição completa (B1) ou validada (B2) | **PARAR** a funcionalidade de exibição até a correção |
| Endossos inseguros do LLM | ≥ 2 em 30 pares auditados, num basket | **AJUSTAR** o juiz; seus rótulos não podem ser usados nem como provisórios sem revisão |
| Confiabilidade especialista | κ ponderado \< 0,60 (estimativa pontual) ou ≥ 2 divergências 0↔3 entre especialistas | **AJUSTAR** a rubrica e repetir a dupla codificação com pares novos |
| Concordância LLM × especialista | κ ponderado \< 0,60 ou ≥ 1 erro 0↔3 | **AJUSTAR** o prompt ou o modelo do juiz |
| Extração | ≥ 1 erro crítico de extração | **AJUSTAR** o extrator e reexecutar os casos afetados |
| Estabilidade | Identidade no top-1 \< 90% ou qualquer mudança de afirmação entre execuções | **AJUSTAR** (fixar sementes, cache, configuração) |
| Viabilidade | Fluxo de endossos fortes projetado \< 450 grupos no estudo completo, ou tempo por avaliação \> 2× o previsto | **AJUSTAR** o desenho do estudo completo (§10) |

**SEGUIR** para o estudo completo se nenhum sinal for acionado, ou se os acionados tiverem sido corrigidos e verificados em casos novos.

### 9.1 O que esses sinais conseguem e não conseguem detectar

Calculado com a binomial exata para a regra "≥ 2 endossos inseguros em 30":

**Tabela 6 — Probabilidade de o juiz passar no sinal**

| Taxa real de endossos inseguros | 0,5% | 1% | 2% | 5% | 10% | 15% |
| :---- | :---- | :---- | :---- | :---- | :---- | :---- |
| P(passar: ≤ 1 em 30\) | 0,99 | 0,96 | 0,88 | 0,55 | 0,18 | 0,05 |

O sinal flagra juízes muito ruins (≥ 10%), mas **não distingue 2% de 0,5%**: essa é a tarefa do plano em dois estágios do estudo completo (§6.4). Passar no piloto não é evidência de que o juiz atende aos critérios do estudo completo.

Da mesma forma, zero erros 0↔3 em 50 pares dá um limite superior de 5,8%, e o IC 95% do κ com 50 pares fica em torno de ±0,08 quando os graus estão razoavelmente balanceados (mais largo se não estiverem). Por isso o κ é julgado pela estimativa pontual, com o intervalo reportado ao lado.

## 10\. Saídas para dimensionar o estudo completo

O relatório final do piloto deve trazer, por basket:

1. **Prevalência dos graus** (0–3 e U) na amostra estratificada e na amostra de endossos fortes.  
2. **Tamanho do fluxo de endossos fortes:** pares e grupos de origem distintos por consulta. Projete quantas consultas o estudo completo precisa para chegar a ≥ 450 grupos independentes (protocolo completo, §6.4); se o número for inviável, o plano de aceitação precisa ser redesenhado antes do estudo completo.  
3. **Tempo médio por avaliação** e taxa de adjudicação, para refazer o orçamento do protocolo completo (§5.3).  
4. **κ observados**, para recalcular o tamanho da amostra de confiabilidade.  
5. **Rendimento das buscas:** artigos triados por caso incluído, por estrato e por `discovery_source`; proporção de pistas do estrato D presentes no índice do Basket 2\.  
6. **Principais classes de erro** (taxonomia do protocolo completo, §7.3) e exemplos com evidência.  
7. **Problemas operacionais:** acesso a textos completos, limitações do 3Ranker e do SMAFIRA, falhas do pipeline.

## 11\. Cronograma sugerido

| Etapa | Atividades | Duração indicativa |
| :---- | :---- | :---- |
| 0 | Aprovar este documento; congelar strings de busca, sementes, versões do motor e do juiz; confirmar se o 3Ranker é componente do Basket 2 | 1 semana |
| 1 | Encontrar e triar os 70 casos (§3) | 2 semanas |
| 2 | Extração de referência e comparação (§4); rodar o motor e o juiz LLM | 1 semana |
| 3 | Sorteio e rotulagem especialista (§§5.2–5.3); adjudicação | 2–3 semanas |
| 4 | Estabilidade (§7); métricas (§8); relatório e decisão (§§9–10) | 1 semana |

Total indicativo: 7–8 semanas, dependendo da disponibilidade dos especialistas.

## 12\. Referências

- **\[R1\]** van Beuningen, N., Alkema, S., Hijlkema, N., Ulfhake, B., Frias, R., Ritskes-Hoitinga, M., & Alkema, W. (2023). The 3Ranker: An AI-based algorithm for finding non-animal alternative methods. *Alternatives to Laboratory Animals, 51*(6), 376–386. [https\://doi.org/10.1177/02611929231210777](https://doi.org/10.1177/02611929231210777)  
- **\[R2\]** Open3R. (s.d.). *3Ranker*. Recuperado em 6 de novembro de 2026, de [https\://www\.open3r.org/](https://www.open3r.org/)  
- **\[R3\]** Neves, M., Klippert, A., Knöspel, F., Rudeck, J., Stolz, A., Ban, Z., Becker, M., Diederich, K., Grune, B., Kahnau, P., Ohnesorge, N., Pucher, J., Schönfelder, G., Bert, B., & Butzke, D. (2023). Automatic classification of experimental models in biomedical literature to support searching for alternative methods to animal experiments. *Journal of Biomedical Semantics, 14*, Artigo 13\. [https\://doi.org/10.1186/s13326-023-00292-w](https://doi.org/10.1186/s13326-023-00292-w) — ferramenta: [https\://smafira.bf3r.de/search](https://smafira.bf3r.de/search)  
- **\[R4\]** Hooijmans, C. R., Tillema, A., Leenaars, M., & Ritskes-Hoitinga, M. (2010). Enhancing search efficiency by means of a search filter for finding all studies on animal experimentation in PubMed. *Laboratory Animals, 44*(3), 170–175. [https\://doi.org/10.1258/la.2010.009117](https://doi.org/10.1258/la.2010.009117)  
- **\[R5\]** Swedish 3Rs Center. (s.d.). *Databases and online resources*. Jordbruksverket. Recuperado em 6 de novembro de 2026, de [https\://jordbruksverket.se/languages/english/the-swedish-3rs-center/for-you-as-a-researcher/databases-and-online-resources](https://jordbruksverket.se/languages/english/the-swedish-3rs-center/for-you-as-a-researcher/databases-and-online-resources)