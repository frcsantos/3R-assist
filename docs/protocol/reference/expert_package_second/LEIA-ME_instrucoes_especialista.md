# Extração de referência — instruções para o especialista (rascunho v0.2)

Piloto de Calibração e Validação (Basket 1), protocolo §4. Você vai ler 30 artigos e registrar, para cada um, **o procedimento com animais descrito** na planilha `extraction_template.xlsx`. Essa extração é a **referência** com que a extração automática será comparada.

## 1. Regras de independência (importante)

1. Trabalhe **sozinho(a)**. Não discuta os casos com o outro especialista até a adjudicação.
2. **Não use ferramentas de IA** (ChatGPT, Claude, Gemini, tradutores com resumo etc.) para ler ou extrair. Dicionários e tradutores de termos pontuais são aceitáveis.
3. Você **não** verá a extração automática do motor e não deve procurá-la.
4. Use **apenas o texto do artigo** fornecido (inclusive tabelas e legendas). Não complete lacunas com conhecimento geral, com o que "costuma ser feito" nem com artigos citados.
5. A pasta contém só o necessário: `sources/` (um arquivo por caso, nomeado RC01 a RC30), esta instrução e a planilha.

## 2. A planilha

`extraction_template.xlsx` tem três abas: **Instrucoes** (resumo), **Extraction** (uma linha por caso) e **Lists** (listas das opções; não edite). Na aba Extraction:

- As colunas `case_id`, `source_file` e `procedure_to_extract` estão **protegidas** (cinza). Se precisar editá-las, use Revisão > Desproteger planilha (sem senha), mas não deve ser necessário.
- Colunas marcadas com **▾** têm **lista suspensa**: escolha um valor da lista. A lista sempre inclui `NOT_STATED`.
- Colunas de texto livre aceitam qualquer texto; escreva `NOT_STATED` quando o texto não informa o dado.
- Passe o mouse sobre o cabeçalho de cada coluna para ver a definição.

## 3. Para cada caso

1. Abra `sources/RCxx.pdf` ou `RCxx.txt` e **inicie o cronômetro**.
2. Leia `procedure_to_extract`: ela diz **qual** procedimento extrair (o artigo pode ter vários). Extraia **somente** esse procedimento. Se existirem outros procedimentos importantes, cite-os em uma linha em `expert_notes`, sem extraí-los.
3. Preencha as colunas usando só o texto do artigo.
4. Preencha `expert_id` e, ao terminar a linha, pare o cronômetro e registre `minutes_spent` (minutos, do primeiro clique até a linha completa).

## 4. Colunas

| Coluna | O que registrar | Formato |
|---|---|---|
| `study_type` | Nome curto do estudo ou modelo | texto livre |
| `procedure_text` | Resumo do procedimento em 1–3 frases, fiel ao texto | texto livre |
| `species` ▾ | Espécie dos animais do procedimento | lista |
| `strain_or_line` | Linhagem, cepa ou linha transgênica | texto livre |
| `sex` ▾ | Sexo dos animais | male, female, both, NOT_STATED |
| `age_or_weight` | Idade e/ou peso na entrada do estudo, com unidade | texto livre |
| `animal_counts_total` | Número total de animais do procedimento | inteiro ou `NOT_STATED` |
| `animal_counts_per_group` | Animais por grupo | número, `n1/n2/n3` ou `NOT_STATED` |
| `route_1` ▾ `route_2` ▾ `route_3` ▾ | Via(s) do procedimento, **uma por coluna**; deixe vazias as não usadas | lista |
| `dose_and_frequency` | Substância(s), dose(s) com unidade e frequência | texto livre |
| `duration_and_timepoints` | Duração do tratamento e momentos de avaliação | texto livre |
| `test_system_1` ▾ `test_system_2` ▾ | Sistema(s) de teste do procedimento, um por coluna | lista |
| `application` ▾ | Finalidade do estudo | lista |
| `endpoints` | Desfechos medidos, separados por `;`, nos termos do artigo | texto livre |
| `regulatory_or_guideline_reference` | Diretriz citada (ex.: `OECD TG 420`) ou `none` | texto |
| `not_stated_fields` | Nomes das colunas cujo dado o texto **não** informa | nomes separados por `;` |
| `inferred_fields` | Nomes das colunas que você **inferiu** do texto | nomes separados por `;` |
| `referenced_fields` | Nomes das colunas que o texto só **remete** a outro trabalho | nomes separados por `;` |
| `ask_for_clarification` ▾ | Você pediria esclarecimento antes de usar este procedimento para buscar um método alternativo? | yes / no |
| `clarification_questions` | Se `yes`: até 3 perguntas objetivas ao autor | texto livre |
| `expert_notes` | Observações; até 2 trechos literais (via, dose, n) entre aspas | texto livre |

O mapeamento dos desfechos para o catálogo de métodos **não** é sua tarefa; a equipe do estudo faz isso depois.

## 5. Desconhecido, inferido e referenciado

Esta distinção é um dos critérios da comparação (§4, item 3):

- **`NOT_STATED`**: o texto não informa o dado. Escolha `NOT_STATED` na lista, ou escreva-o no campo de texto. Não preencha com valor provável. Cite o nome da coluna em `not_stated_fields`.
- **Inferido**: o dado não está escrito, mas decorre do texto (ex.: 20 animais em 2 grupos iguais, logo 10 por grupo). Preencha o valor, cite a coluna em `inferred_fields` e explique em `expert_notes`. Use com parcimônia.
- **Referenciado**: o texto remete a outro trabalho ("como descrito anteriormente [12]") em vez de descrever. Não busque a referência: escreva `NOT_STATED` no campo e cite a coluna em `referenced_fields`.

## 6. Observações sobre as listas

- `route`: anestesia, sedação e eutanásia **não** contam como via do procedimento, salvo se forem o objeto do estudo. Se a via não for relevante (exposição ambiental, cirurgia etc.), use `not-applicable`.
- `species`: use `other` para espécies que não estão na lista.
- `test_system`: `in_vivo` para o procedimento com animais; acrescente `ex_vivo` etc. em `test_system_2` só se o procedimento incluir também esse sistema.

## 7. Pedir esclarecimento (`ask_for_clarification`)

Responda `yes` quando faltar informação que **impeça** descrever o procedimento para buscar métodos alternativos (por exemplo, espécie, substância, dose ou via, ou desfecho não identificáveis). Responda `no` quando o procedimento estiver descrito o bastante, mesmo que detalhes secundários faltem. Em caso de dúvida, escolha e explique em `expert_notes`.

## 8. Entrega

Salve a planilha como `extraction_<expert_id>.xlsx` e devolva-a à equipe. Não altere `case_id`, `source_file` nem `procedure_to_extract`. Dúvidas sobre **o procedimento** de um caso: anote em `expert_notes`; não contate o outro especialista.
