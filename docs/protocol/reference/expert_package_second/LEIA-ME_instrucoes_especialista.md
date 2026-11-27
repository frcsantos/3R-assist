# Extração de referência — instruções para o especialista (rascunho v0.1)

Piloto de Calibração e Validação (Basket 1), protocolo §4. Você vai ler 30 artigos e registrar, para cada um, **o procedimento com animais descrito** nos campos da planilha `extraction_template.csv`. Essa extração é a **referência** com que a extração automática será comparada.

## 1. Regras de independência (importante)

1. Trabalhe **sozinho(a)**. Não discuta os casos com o outro especialista até a adjudicação.
2. **Não use ferramentas de IA** (ChatGPT, Claude, Gemini, tradutores com resumo etc.) para ler ou extrair. Dicionários e tradutores de termos pontuais são aceitáveis.
3. Você **não** verá a extração automática do motor e não deve procurá-la.
4. Use **apenas o texto do artigo** fornecido (inclusive tabelas e legendas). Não complete lacunas com conhecimento geral, com o que "costuma ser feito" nem com artigos citados.
5. A pasta contém só o necessário: `sources/` (um arquivo por caso, nomeado RC01 a RC30), esta instrução e a planilha.

## 2. Para cada caso

1. Abra `sources/RCxx.pdf` ou `RCxx.txt` e **inicie o cronômetro**.
2. Leia a coluna `procedure_to_extract` da planilha: ela diz **qual** procedimento extrair (o artigo pode ter vários). Extraia **somente** esse procedimento. Se outros procedimentos importantes existirem, anote-os em `expert_notes` em uma linha, sem extraí-los.
3. Preencha os campos da seção 3 usando só o texto do artigo.
4. Preencha `expert_id` e, ao terminar a linha, pare o cronômetro e registre `minutes_spent` (minutos, do primeiro clique até a linha completa).

## 3. Campos

| Campo | O que registrar | Valores / formato |
|---|---|---|
| `study_type` | Nome curto do estudo ou modelo | texto livre |
| `procedure_text` | Resumo do procedimento em 1–3 frases, fiel ao texto | texto livre |
| `species` | Espécie dos animais do procedimento | lista da seção 5 (`other` se não houver) |
| `strain_or_line` | Linhagem, cepa ou linha transgênica | texto livre |
| `sex` | Sexo dos animais | `male`, `female`, `both` ou convenção da seção 4 |
| `age_or_weight` | Idade e/ou peso na entrada do estudo | com unidade (ex.: `8–10 weeks; 20–25 g`) |
| `animal_counts_total` | Número total de animais do procedimento | número inteiro |
| `animal_counts_per_group` | Animais por grupo | número ou `n1/n2/n3` |
| `route` | Via(s) de administração/exposição | lista da seção 5; várias separadas por `;` |
| `dose_and_frequency` | Substância(s), dose(s) com unidade e frequência | texto livre |
| `duration_and_timepoints` | Duração do tratamento e momentos de avaliação | texto livre |
| `test_system` | Sistema de teste do procedimento | lista da seção 5; vários separados por `;` |
| `application` | Finalidade do estudo | lista da seção 5 |
| `endpoints` | Desfechos medidos, separados por `;` | texto livre, nos termos do artigo |
| `regulatory_or_guideline_reference` | Diretriz citada (ex.: `OECD TG 420`) ou `none` | texto |
| `unknown_or_not_stated_items` | Lista dos campos que o texto **não** informa | nomes de campos separados por `;` |
| `ask_for_clarification_yes_no` | Você pediria esclarecimento antes de usar este procedimento para buscar um método alternativo? | `yes` ou `no` |
| `clarification_questions` | Se `yes`: até 3 perguntas objetivas ao autor | texto |
| `expert_notes` | Observações; até 2 trechos literais (via, dose, n) entre aspas | texto livre |

O mapeamento dos desfechos para o catálogo de métodos **não** é sua tarefa; a equipe do estudo faz isso depois.

## 4. Desconhecido, inferido e referenciado

Esta distinção é um dos critérios da comparação (§4, item 3). Use sempre:

- **`NOT_STATED`**: o texto não informa o dado. Não preencha com valor provável.
- **`INFERRED: <valor> (<motivo>)`**: o dado não está escrito, mas decorre do texto (ex.: `INFERRED: 10 per group (n=20 in 2 equal groups)`). Use com parcimônia.
- **`REFERENCED: <citação>`**: o texto remete a outro trabalho ("como descrito anteriormente [12]") em vez de descrever. Não busque a referência.

Todo campo `NOT_STATED` ou `REFERENCED` deve constar em `unknown_or_not_stated_items`.

## 5. Vocabulários

- **species**: human, rat, mouse, rabbit, guinea_pig, dog, bovine, chicken, zebrafish, rainbow_trout, horseshoe_crab, salmonella_typhimurium, escherichia_coli, horse, tachypleus_tridentatus, in_vitro, other
- **route**: cutaneous, inhalation, oral, ocular, intranasal, intratracheal, intravenous, intra-arterial, intramuscular, subcutaneous, intradermal, intraperitoneal, rectal, vaginal, topical-mucosal, implantation, multiple, not-applicable, unspecified, other, aquatic-waterborne
- **test_system**: in_vivo, ex_vivo, in_vitro, in_chemico, in_silico, in_data
- **application**: basic-research, translational-applied-research, regulatory-use, routine-production, education-training, environmental-protection, species-preservation, forensic-inquiry, diagnostic-testing, other

Anestesia, sedação e eutanásia **não** contam como `route` do procedimento, salvo se forem o objeto do estudo. Se a via do procedimento não for relevante (p. ex., exposição ambiental ou cirurgia), use `not-applicable`.

## 6. Pedir esclarecimento (`ask_for_clarification_yes_no`)

Responda `yes` quando faltar informação que **impeça** descrever o procedimento para buscar métodos alternativos (por exemplo, espécie, substância, dose ou via, ou desfecho não identificáveis). Responda `no` quando o procedimento estiver descrito o bastante, mesmo que detalhes secundários faltem. Em caso de dúvida, escolha, e explique em `expert_notes`.

## 7. Entrega

Salve a planilha como CSV UTF-8 com o nome `extraction_<expert_id>.csv` e devolva-a à equipe. Não altere `case_id`, `source_file` nem `procedure_to_extract`. Dúvidas sobre **o procedimento** de um caso: anote em `expert_notes`; não contate o outro especialista.
