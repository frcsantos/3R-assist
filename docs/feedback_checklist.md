# Checklist do feedback dos usuários

Gerado a partir da tabela `feedback` (26 registros, 11/08/2026 a 29/09/2026), comparando cada pedido com o estado atual do banco. Os registros da tabela não foram alterados.

Legenda: `[x]` já resolvido ou não é mais relevante. `[ ]` ainda pendente. `(decisão)` depende de uma decisão da curadoria, listada em [decisoes_curadoria.md](decisoes_curadoria.md).

Observações que valem para vários itens:
- **Todos os métodos, exceto o GD 129, estão com `active = false`.** Só o GD 129 aparece hoje na aplicação.
- **Títulos:** os pedidos escrevem o título como na resolução, com o prefixo "Método OECD TG nnn - …". Decisão tomada: manter os títulos atuais (sem o prefixo, migrations 068 a 070). Os itens de título estão marcados como mantidos.
- **Status de validação:** "Reconhecido" (pedido em 11 registros) foi adicionado ao vocabulário (`recognized`, migration 078), mas os 47 métodos continuam `validated`. Falta decidir quais passam a `recognized` (decisão, ver #6 e o item 8 de decisoes_curadoria.md).
- **Referência da RN:** todos os métodos têm uma regulação do Brasil com o documento da RN que o reconhece, agora com data de publicação, vigência e prazo de substituição (`regulations`, migrations 081 e 087). O que não consegui verificar é se a interface mostra isso.
- **Revisão:** os 47 métodos estão com `review_status = in_review` (migration 086); nenhum está `reviewed`.
- **Sem feedback novo:** a tabela `feedback` continua com os mesmos 26 registros (o último é de 29/09/2026).

## Testes e itens sem ação
- [x] #1 "hello" (Test Method): teste, descartar.
- [x] #2 "teste" (TG 423): teste, descartar.
- [x] #4 "teste" (LAL): teste, descartar.
- [x] #3 GD 129: "justificativa da redução em inglês". A justificativa em pt-br está em português.

## Status de validação (vale para vários métodos)
- [ ] #6 dRIT: hierarquia proposta pelos usuários: Validado (aceitação internacional), Reconhecido (específico do Brasil), Em processo de validação, Descrito na literatura científica, Descrito na literatura cinzenta. (decisão) Afeta #10, #11, #12, #13, #14, #22, #23, #24, #25 e #26, que pedem "Reconhecido" para cada método.
- [ ] #10 TG 438: status regulatório "reconhecido no Brasil". (decisão, ver #6)

## Rabies (DFA, dRIT, RTCIT, RT-PCR)
O pedido de aplicação "teste diagnóstico" já está atendido nos quatro (aplicação 10).

### dRIT (método 33), #5
- [x] Aplicação "teste diagnóstico".
- [x] Categoria de desfecho "diagnóstico da raiva animal" (endpoint "Diagnóstico da raiva").
- [x] Título e descrição em português: o pt-br existe.
- [x] Título (mantido, decisão de manter os títulos): "Teste Rápido de Imuno-histoquímica Direta (Direct Rapid Immunohistochemistry Test) - dRIT". Hoje: "Teste rápido de imuno-histoquímica direta (dRIT) para diagnóstico da raiva".
- [ ] Uso de animais: "abatedouro" está errado. Sugestão dos usuários: "potencial uso de insumos de origem animal". O material do método agora está em `method_materials` (tecido do sistema nervoso central de animais suspeitos). (decisão, ver item 3 de decisoes_curadoria.md)
- [x] Sistema de teste: de `ex_vivo` para `in_vitro` (migration 077).

### RT-PCR (método 35), #12
- [x] Aplicação "teste diagnóstico".
- [x] Título (mantido, decisão de manter os títulos): "Técnicas moleculares baseadas em Reação de Transcriptase Reversa, seguida de Reação em Cadeia da Polimerase quantitativa (RT-qPCR) ou convencional (RT-PCR)".
- [x] Descrição (migration 076): trocar "Destina-se a substituir testes de inoculação em camundongos para isolamento viral." por "Pode substituir o teste de inoculação em camundongos (Mouse inoculation Test - MIT) para diagnóstico da raiva animal."
- [ ] Uso de animais: de `slaughterhouse_byproduct` para misto ou variável (`mixed_or_variable`). (decisão, ver item 3 de decisoes_curadoria.md)
- [ ] Status: reconhecido no Brasil. (decisão, ver #6)

### DFA (método 30), #13
- [x] Aplicação "teste diagnóstico".
- [x] Nome (mantido, decisão de manter os títulos): "Técnica de Imunofluorescência Direta (Direct Fluorescent Antibody Test) - DFA Test".
- [x] Descrição (migration 076): "Técnica de diagnóstico laboratorial utilizada para detectar antígenos do vírus da raiva em impressões ou esfregaços de tecido cerebral, por meio de anticorpos anti-rábicos conjugados à fluoresceína."
- [ ] Uso de animais: misto ou variável. (decisão, ver item 3 de decisoes_curadoria.md)
- [x] Sistema de teste: `in_vitro` (migration 077).
- [ ] Status: reconhecido. (decisão, ver #6)

### RTCIT (método 34), #14
- [x] Aplicação "teste diagnóstico".
- [x] Nome (mantido, decisão de manter os títulos): "Isolamento viral em cultivo celular (Rabies Tissue Culture Infection Test - RTCIT)".
- [ ] Uso de animais: misto ou variado. (decisão, ver item 3 de decisoes_curadoria.md)
- [ ] Status: reconhecido. (decisão, ver #6)

## GD 129 (método 22), #15, #16, #20, #3, #17
- [x] #15 Título (mantido, decisão de manter os títulos): "Método OECD TG 129 - estimativa da dose inicial para teste de toxicidade aguda oral sistêmica". Os usuários perguntam se devem manter "TG" como na RN 18 do CONCEA, ainda que o correto seja "GD" (Guidance Document). A pergunta fica sem efeito enquanto o título atual for mantido.
- [x] #16 Descrição (migration 076): substituir pela proposta ("Ensaio de citotoxicidade basal in vitro baseado na captação de vermelho neutro (NRU), utilizando células BALB/c 3T3 ou queratinócitos humanos normais (NHK)…").
- [x] #16 "Substituição" incluída como R (`replacement_rationale`, migration 076), com texto condicionado ao regulador.
- [ ] #20 Uso de animais: dizer que usa produto de origem animal (provável `animal_derived_material`). (decisão, ver item 5 de decisoes_curadoria.md)
- [x] #17 Referência da RN 18: o método tem a regulação do Brasil com a RN 18/2014. (a exibição na interface não foi verificada)

## Pele
### Corrosão cutânea RHE, TG 431 (método 3), #18, #21
- [x] #18 Título (mantido, decisão de manter os títulos): "Corrosão dérmica in vitro: Teste da Epiderme Humana Reconstituída".
- [x] #18 Descrição (migration 076): "Método in vitro que utiliza epiderme humana reconstruída tridimensional, com estrato córneo funcional, para identificar substâncias e misturas corrosivas e não corrosivas com base na redução da viabilidade celular após períodos definidos de exposição."
- [x] #18 Categoria de desfecho "corrosão cutânea": o endpoint do método já é esse.
- [ ] #21 Uso de animais: misto ou variável (hoje `NULL`). (decisão, ver item 6 de decisoes_curadoria.md)

### TER, TG 430 (método 4), #22
- [x] Título (mantido, decisão de manter os títulos): "Corrosão dérmica in vitro: teste de resistência elétrica transcutânea".
- [x] Uso de animais: animais mortos para obtenção de tecidos (migration 074).
- [x] Categoria de desfecho "corrosão cutânea".
- [ ] Trocar de substituição para redução e refinamento. (decisão, ver item 7 de decisoes_curadoria.md)
- [ ] Status: reconhecido. (decisão, ver #6)

### Barreira de membrana, TG 435 (método 5), #23
- [x] Título (mantido, decisão de manter os títulos): "Teste de barreira de membrana in vitro".
- [x] Descrição (migration 076): "…semelhante à pele…" em vez de "…semelhante à pele animal in situ…".
- [x] Categoria de desfecho "corrosão cutânea".
- [x] Referência da RN 18: o método tem a regulação do Brasil com a RN 18/2014.
- [ ] Status: reconhecido. (decisão, ver #6)

### Irritação cutânea, TG 439 (método 1), #24
- [x] Título (mantido, decisão de manter os títulos): "Teste de irritação cutânea in vitro".
- [x] Referência da RN 18.
- [ ] Status: reconhecido. (decisão, ver #6)

### LLNA, TG 429 (método 13), #7
- [x] Título (mantido, decisão de manter os títulos): "Sensibilização Cutânea: Ensaio do Linfonodo Local". Hoje: "Ensaio do Linfonodo Local (LLNA)".

### DPRA, TG 442C (método 10), #11
- [x] Título: "Sensibilização cutânea in chemico", igual à resolução (sem o prefixo).
- [x] Descrição (migration 076): trocar "evento iniciador molecular" por "evento molecular inicial".
- [x] Referência: o método tem a regulação do Brasil, pela RN 31/2016. O pedido cita "RN 32", que não é a resolução que reconhece o TG 442C.
- [ ] Status: reconhecido no Brasil. (decisão, ver #6)

### Fototoxicidade 3T3 NRU, TG 432 (método 16), #26
- [x] Título: "Teste de Fototoxicidade in vitro 3T3 NRU", igual à resolução.
- [x] Descrição (migration 076): trocar "foto-citotoxicidade" por "fototoxicidade" e acrescentar "(linhagem de fibroblastos murinos)" depois de "Balb/c 3T3".
- [ ] Uso de animais: material derivado de animal (`animal_derived_material`). (decisão, ver item 5 de decisoes_curadoria.md)
- [x] Referência da RN 18.
- [ ] Status: reconhecido. (decisão, ver #6)

## Olho
### BCOP, TG 437 (método 6), #8
- [x] Título: "Teste de Permeabilidade e Opacidade de Córnea Bovina (BCOP)", igual à resolução (migration 069).
- [x] Descrição (migration 076): trocar "um método de teste in vitro" por "um método de teste ex vivo".
- [x] Categoria "irritação e corrosão ocular": o método tem os endpoints "Irritação ocular" e "Danos oculares graves".

### ICE, TG 438 (método 7), #9, #10
- [x] Título: "Teste de Olho Isolado de Galinha", igual à resolução (migration 069).
- [x] Descrição (migration 076): trocar "um método de teste in vitro" por "um método de teste ex vivo".
- [x] Categoria "irritação e corrosão ocular".
- [x] Referência da RN 18.
- [ ] #10 Status regulatório "reconhecido no Brasil". (decisão, ver #6)

### Fluoresceína, TG 460 (método 8), #25
- [x] Título (mantido, decisão de manter os títulos): "Teste de permeação de fluoresceína".
- [x] Categoria "corrosão ocular": o método tem o endpoint "Danos oculares graves".
- [x] Referência da RN 18.
- [ ] Status: reconhecido. (decisão, ver #6)

## Endócrino
### TG 455 (método 41), #19
- [x] Nome (mantido, decisão de manter os títulos): "Teste baseado na performance para ensaios in vitro de transativação transfectada estável para detectar agonistas e antagonistas de receptor estrogênico".
- [x] Descrição (migration 076): substituir por "Diretriz baseada em desempenho para ensaios in vitro com linhagens celulares estavelmente transfectadas, utilizados para identificar substâncias com atividade agonista ou antagonista sobre receptores de estrogênio por meio da transativação de gene repórter."
- [ ] Uso de animais: misto ou variável. (decisão, ver item 5 de decisoes_curadoria.md)
- [x] Referência da RN 56/2022 com o link: o documento 5 tem o link do DOU, igual ao do pedido.

## Resumo
- **Resolvidos ou irrelevantes:** 3 testes descartados, a justificativa em inglês do GD 129, as aplicações dos métodos de raiva, as categorias de desfecho, o uso de animais do TER, as referências das RNs, as descrições pedidas, a "substituição" do GD 129 e o `test_system` da raiva.
- **Títulos:** todos os pedidos de título foram marcados como mantidos, por decisão de manter os títulos atuais.
- **Pendentes de decisão da curadoria:** status de validação (#6, afeta 11 métodos), `animal_use` dos métodos de raiva, GD 129, TG 431, TG 432 e TG 455, e os 3Rs do TER. Todos estão em [decisoes_curadoria.md](decisoes_curadoria.md).
