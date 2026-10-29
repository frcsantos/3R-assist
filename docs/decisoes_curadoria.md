# Decisões pendentes da curadoria

Todas as pendências que dependem de decisão da curadoria, reunidas num só lugar: `animal_use`, 3Rs, status de validação e regulatório, vocabulário de `test_system`, mapeamento OHT, nomes, campos novos e confirmações. O plano de revisão (`Revisao.md`) é a referência para as categorias e critérios. As regras de `animal_use` estão no ADR-026 (`docs/decisions.md`). Nada abaixo foi aplicado no banco, exceto os itens 1 e 18 (migration 118), os itens 2, 5 e 6 (migration 119) e o TG 428 do item 7 (migration 120), aplicados provisoriamente e marcados para confirmação. O apêndice traz o comparativo entre os títulos dos métodos e o texto das resoluções do CONCEA.

As classificações foram analisadas sem a fonte completa das TGs (os PDFs em `docs/oecd_files` têm só o resumo), então cada item precisa ser confirmado nos protocolos.

Como registrar a decisão: marque a opção escolhida e, depois, a mudança vai para uma migration.

| # | Tema | Métodos ou tabelas |
|---|---|---|
| 1 | S9 nas TGs de genotoxicidade | `animal_use` das TG 471, 473, 476, 487 e 490 |
| 2 | TG 492 e TG 492B | `animal_use` |
| 3 | Diagnóstico de raiva | `animal_use` dos métodos 30, 33, 34 e 35 |
| 4 | TG 435, 494 e 496 | `animal_use` |
| 5 | Soro animal (SFB) | `animal_use` de 8 métodos |
| 6 | Possíveis `none` | `animal_use` |
| 7 | Rationale dos 3Rs | `replacement_`, `reduction_` e `refinement_rationale` |
| 8 | Status de validação | vocabulário de `validation_status` |
| 9 | Valor `in_data` | `test_system` |
| 10 | Mapeamento OHT | `endpoints.external_oht_codes` e catálogo de métodos |
| 11 | Confirmações e verificações | vários |
| 12 | Nomes dos métodos (pt-br e en-us) e TG 442D e 442E | `methods.name` |
| 13 | Campos exigidos pelo plano e que não existem | tabela `methods` |
| 14 | Finalidade e contexto de aplicação | `applications` e `methods.application_ids` |
| 15 | Endpoints | `methods.endpoints` |
| 16 | Status regulatório `recognized` | `regulations.regulatory_status` |
| 17 | TG 319A e 319B: substituição ou redução | `animal_procedures_avoided` e rationales dos métodos 54 e 55 |
| 18 | Valor `embryos_and_larvae` | `animal_use` dos métodos 51 (TG 212) e 53 (TG 236) |

Decididos e já aplicados (não precisam de ação):
- Sistema de teste: `hybrid` removido (migration 078). As categorias são `in_silico`, `in_chemico`, `in_data`, `in_vitro`, `ex_vivo`, `in_vivo` e `unclear`.
- Status de validação: `recognized` adicionado e `not_evaluated` removido; o padrão de métodos novos passou a ser `unclear` (migration 078, ver item 8).
- Status regulatório: `recognized` adicionado (migration 078, ver item 16).
- Endpoints: adicionados os mais específicos, mantendo os gerais (migration 078, ver item 15).
- Finalidade e contexto de aplicação (migration 080): MAT, LAL e rFC receberam "Produção de rotina"; TG 212, 236, 319A e 319B receberam "Proteção do meio ambiente natural" (todos mantêm "Uso regulatório"). O rótulo pt-br de `education-training` passou a "Educação e treinamento". A categoria `diagnostic-testing` agora existe no código e na documentação, e o código lê a lista da tabela `applications` em vez de tê-la fixa.
- 3Rs: cada `replacement_rationale` agora diz se a substituição é total ou parcial (migration 079, ver item 7), e o glossário tem as definições de substituição total e parcial.

## 1. S9 nas TGs de genotoxicidade

- **Métodos:** TG 471, 473, 476, 487 e 490.
- **Situação:** todos usam ativação metabólica com S9 de fígado de rato. Só o TG 490 está `animals_killed_for_tissue`. Os outros quatro estão `NULL`.
- **O que os textos completos dizem (TG 471, 473, 476, 487 e 490):** o S9 é preparado de fígado de roedores (geralmente ratos) tratados com indutores enzimáticos (Aroclor 1254 ou fenobarbital com β-naftoflavona). É o sistema recomendado por padrão nas TGs 473, 476, 487 e 490 (a TG 487 admite outro sistema, se justificado) e o mais usado na TG 471. Nenhuma das cinco fala em S9 comercial. Os registros estão em `method_materials`.
- **Aplicado provisoriamente (migration 118):** assumido S9 preparado no laboratório. Os métodos 17, 18, 19 e 45 passaram de `NULL` para `animals_killed_for_tissue`, como o TG 490 (46). **A confirmar.**
- **Decisão:** definir um valor único para os cinco.
  - [ ] `animal_derived_material`, se o S9 for comercial (regra 4 do ADR).
  - [ ] `animals_killed_for_tissue`, se o S9 for preparado no laboratório.
  - [ ] `mixed_or_variable`, se o uso variar entre os laboratórios.

## 2. TG 492 e TG 492B

- **Métodos:** 9 (TG 492) e 39 (TG 492B).
- **Situação:** os dois usam o mesmo tipo de modelo (RhCE). O TG 492 está `animal_derived_material` e o TG 492B está `NULL`.
- **Modelos citados nas TGs:** TG 439: EpiDerm SIT, EpiSkin, SkinEthic RHE, LabCyte EPI-MODEL24 SIT, epiCS, Skin+ e KeraSkin. TG 431: EpiSkin, EpiDerm SCT, SkinEthic RHE, epiCS e EST-1000. TG 492: EpiOcular, SkinEthic HCE, LabCyte CORNEA-MODEL24 e MCTT HCE. Já estão no repositório o manual do LabCyte EPI-MODEL (o meio de ensaio do kit "contém soro", espécie não informada; modelo feito de células epidérmicas humanas normais), o protocolo 135 do DB-ALM do SkinEthic RHE (queratinócitos humanos normais em filtro de policarbonato, "meio de crescimento quimicamente definido", sem menção a soro nem a outro componente animal) o protocolo 131 do DB-ALM do EpiSkin SIT e a página do TSAR do epiCS (EST-1000). O EpiSkin-SM usa queratinócitos de doadores voluntários humanos saudáveis sobre um substituto dérmico de colágeno tipo I revestido com colágeno tipo IV, e os meios do kit (manutenção e ensaio) vêm prontos, sem composição; o protocolo não cita soro e não diz a espécie do colágeno. O epiCS só tem a descrição do modelo. Ou seja, os meios dos modelos variam: o LabCyte tem soro, o SkinEthic é quimicamente definido, e o EpiSkin e o epiCS não informam; e o colágeno do EpiSkin é um componente de origem possivelmente animal, sem origem declarada. Isso sustenta o pedido dos usuários de `mixed_or_variable` para o TG 431 (feedback #21) e se aplica igualmente ao TG 439.
- **Modelos da TG 492/492B e EpiSensA (protocolos 164, 190, 191 e SOP v2.6):** o EpiOcular (protocolo 164) é feito de queratinócitos humanos normais derivados de prepúcio, não transformados, em "meio especializado" sem composição nem menção a soro. O SkinEthic HCE (protocolos 190 EITL e 191 EITS) usa uma linhagem humana transformada de epitélio corneano, cultivada em "meio quimicamente definido", sem menção a soro. O SOP do EpiSensA (Kao, v2.6) usa o kit LabCyte EPI-MODEL24 (J-TEC 401124, queratinócitos epidérmicos humanos normais) com meio de ensaio pronto, sem composição (o manual do kit diz que contém soro). A planilha de dados do EpiSensA é só um modelo de cálculo e não traz informação de materiais. Notas dos materiais atualizadas na migration 106. Em nenhum dos três há componente animal declarado, mas o EpiOcular e o EpiSensA não informam o meio, então a classificação `animal_use` desses métodos continua dependendo da regra da decisão #5.
- **LabCyte (documentos do JaCVAM/J-TEC):** os SOPs do EPI-MODEL24 (SIT v8.3, SCT v1.6, SIT para extratos de dispositivos v2.2), o relatório do painel de revisão por pares do SCT (2018) e o protocolo do CORNEA-MODEL24 (v2.7) dizem que o tecido é cultivado por 13 dias na interface ar-líquido em "meio otimizado contendo 5% de soro fetal bovino". Isso fixa a espécie do soro (bovina) e contradiz a leitura anterior de que o LabCyte seria o único com soro "de espécie não informada". Os queratinócitos (prepúcio neonatal) e as células epiteliais da córnea (córnea de doador humano) são expandidos sobre células alimentadoras 3T3-J2 irradiadas; os documentos não dizem a espécie (a 3T3-J2 é uma linhagem de fibroblastos de camundongo, a confirmar). O manual do kit já dizia que o meio de ensaio contém soro. Registrado na migration 107 (soro bovino e células alimentadoras de camundongo em TG 439, TG 442D e TG 492, com `animal_derived` verdadeiro). A migration 107 e a 106 também tinham aplicado esses modelos à TG 492B; isso foi um erro, porque o texto da TG 492B descreve só o teste de tempo até a toxicidade (TTT) do SkinEthic HCE, sem EpiOcular, LabCyte nem MCTT. A migration 108 removeu as linhas do LabCyte do método da TG 492B e corrigiu a nota. Consequência para a decisão #5: os métodos que listam o LabCyte têm componente animal declarado, mas é um modelo entre vários da mesma diretriz, então a regra de `mixed_or_variable` ou de `animal_derived_material` continua com a curadoria. O SOP do SIT para extratos de dispositivos médicos (v2.2) é fora do escopo do catálogo de TGs e não foi usado. O LabCyte SCT (peer review 2018, "dentro da TG 431") não está na lista de modelos da TG 431 que o catálogo usa; confirmar se uma versão posterior da TG 431 o inclui antes de adicioná-lo ao método 3.
- **MCTT HCE e KeraSkin (SOPs do KoCVAM/Biosolution):** o MCTT HCE (TG 492; SOP v1.8 de 2024, protocolo v1.7 e ficha do produto MM331) usa células epiteliais corneanas humanas normais derivadas de córnea humana normal, cultivadas por 14 dias em insertos Millicell e enviadas sobre gel de agarose com o meio de ensaio. O KeraSkin (TG 439; SOP da fototoxicidade v1.3, 2025) usa queratinócitos humanos primários de origem coreana, também sobre agarose. Nenhum dos dois documentos descreve a composição do meio nem cita soro, então não há componente animal declarado (a agarose é um gel vegetal de transporte). O MCTT HCE já consta na TG 492 e a página do TSAR (validação "em andamento") está desatualizada. A TG 498 (edição de 2026, já na pasta) inclui o KeraSkin Phototoxicity Assay como método "me-too" do EpiDerm PT (sensibilidade 100%, especificidade 98,6%, acurácia 99,3%) e cita o SOP v1.3 e o relatório de revisão por pares da OCDE, o que reforça a TG 498 como candidata ao catálogo (item 10). Notas dos materiais atualizadas na migration 108.
- **Meio do EpiOcular e protocolos TTL/TTS do SkinEthic HCE (migration 109):** a página técnica da MatTek diz que o EpiOcular usa queratinócitos epidérmicos humanos normais de um único doador (prepúcio neonatal), em meio com base DMEM, fator de crescimento epidérmico, insulina, hidrocortisona e outros estimuladores proprietários, e afirma "Serum: None" (sem soro); acrescenta gentamicina e anfotericina B. A espécie da insulina e do fator de crescimento não é informada. Os protocolos TTL e TTS do SkinEthic HCE (DB-ALM, versão 2, junho de 2020, os SOPs que a TG 492B cita) confirmam a linhagem humana transformada de epitélio corneano em "meio quimicamente definido", de composição proprietária (ficha técnica enviada pelo fornecedor), sem citar soro. Notas: o arquivo "DBALM HCE TTS_November 2021" traz no texto "última atualização: junho de 2020" e o TTS ainda usa ácido lático a 1% como controle positivo, enquanto o TTL passou a usar acetato de metila. Juntando tudo, o único modelo da TG 492 com soro declarado é o LabCyte CORNEA-MODEL24 (soro fetal bovino a 5% e células alimentadoras 3T3-J2); EpiOcular, SkinEthic HCE e MCTT HCE não declaram componente animal. Os dois resumos da L'Oréal/Episkin (2010 e 2011, sobre o protocolo antigo de 1 h e o ensaio de ligação a peptídeos RPBA-HCE) só servem como referência histórica e não trazem dados de materiais.
- **Onde achar os protocolos dos modelos (referências das próprias TGs):**
  - O **EpiSkin não está mais disponível comercialmente**: foi retirado da lista de modelos da TG 439 (atualização de 2024/5) e da TG 431 (2025), mas os dados gerados com ele continuam cobertos pela aceitação mútua de dados.
  - TG 439: SOP do EpiDerm SIT (versão 7.0) e do SkinEthic RHE (versão 2.0), no site do JRC; SOP do Skin+ (Sterlab, versão 5.0) em sterlab-store.com; SOP do epiCS (CellSystems, versão 5.1) em reconstructed-human-epidermis.com; SOP do KeraSkin SIT (versão 1.5) em keraskin.co.kr; SOP do LabCyte EPI-MODEL24 SIT (JaCVAM).
  - TG 431: SOPs do EpiDerm SCT, do SkinEthic RHE, do epiCS (versão 4.1) e do LabCyte EPI-MODEL24 SCT (versão 1.6, em jacvam.jp).
  - TG 492: SOPs do EpiOcular EIT (versão 8), do SkinEthic HCE EIT, do LabCyte CORNEA-MODEL24 EIT (jacvam.jp) e do MCTT HCE EIT (keraskin.co.kr). TG 492B: SOPs do SkinEthic HCE Time-to-Toxicity (episkin.com).
- **O que os textos completos dizem (TG 492 e 492B):** não citam soro nem outro componente de origem animal; a composição dos meios dos modelos é proprietária. Para decidir é preciso o protocolo do fabricante do modelo (ou o método de referência validado), que não está no repositório.
- **Aplicado provisoriamente (migration 119):** TG 439, TG 431 e TG 442D (métodos 1, 3 e 11), que usam modelos RhE, passaram de `NULL` para `mixed_or_variable`, porque o meio varia entre os modelos (LabCyte com FBS a 5% e células alimentadoras 3T3-J2; SkinEthic quimicamente definido). **A confirmar.** O TG 492B (método 39) continua `NULL`.
- **Decisão:** usar o mesmo valor nos dois.
  - [ ] `animal_derived_material`
  - [ ] `none`

## 3. Diagnóstico de raiva

- **Métodos:** 30 (DFA), 33 (dRIT), 34 (RTCIT) e 35 (RT-PCR).
- **Situação:** os quatro estão `slaughterhouse_byproduct`, mas o material é cérebro de animal com suspeita de raiva, e não de abatedouro. O `test_system` já foi igualado em `in_vitro` nos quatro (migration 077).
- **O que o capítulo 3.1.19 da WOAH (2023) diz:**
  - O material é tecido do sistema nervoso central retirado do crânio de animais suspeitos (tronco encefálico, corno de Ammon, tálamo, córtex, cerebelo e bulbo). Não é material de abatedouro.
  - O DFA e o dRIT usam anticorpos policlonais ou monoclonais anti-rábicos marcados (FITC no DFA, biotina no dRIT). Os policlonais vêm de animais imunizados.
  - O RTCIT usa células de neuroblastoma, como N2a (ATCC CCL-131), em DMEM com 5% de soro fetal de bezerro, e soro fetal de bezerro inativado no homogenato de cérebro.
  - O teste de inoculação em camundongos (MIT) usa de 3 a 10 camundongos de 3 a 4 semanas, ou uma ninhada de recém-nascidos de 2 dias, com inoculação intracerebral. A WOAH o mantém como teste confirmatório, quando os testes primários (DFA, dRIT, RT-PCR pan-lyssavirus) são inconclusivos, e diz que o isolamento viral em cultura de células deve substituí-lo sempre que possível, porque é tão sensível quanto, mais rápido, mais barato e evita o uso de animais.
  - Isso está em `method_materials` e em `animal_procedures_avoided` (migration 095).
- **Pedidos dos usuários (feedback #5, #12, #13, #14):** DFA, RT-PCR e RTCIT como "misto ou variável"; dRIT como "potencial uso de insumos de origem animal".
- **Decisão:** classe de `animal_use`.
  - [ ] `mixed_or_variable` nos quatro (pedido dos usuários).
  - [ ] `mixed_or_variable` em DFA, RT-PCR e RTCIT, e `animal_derived_material` no dRIT.
  - [ ] Manter `slaughterhouse_byproduct`.
  - [ ] Criar uma classe nova (exigiria mudar a CHECK constraint).

## 4. TG 435, 494 e 496

- **Métodos:** 5 (TG 435), 47 (TG 494) e 49 (TG 496).
- **Situação:** os três estão `NULL`. Provavelmente deveriam ser `animal_derived_material`, por causa de colágeno e queratina (TG 435), membrana de colágeno (TG 494) e matriz proteica (TG 496).
- **O que os textos completos dizem:** a TG 435 descreve um gel proteico "composto de proteína, por exemplo queratina, colágeno ou misturas de proteínas", sem dizer a origem; a TG 494 usa uma membrana de colágeno vitrigel, sem dizer a origem do colágeno, e meio com 5% de soro fetal bovino inativado; a TG 496 usa um reagente acelular de proteínas, glicoproteínas, carboidratos e lipídios, sem dizer a origem. A origem dos componentes das TGs 435 e 496 e do colágeno da TG 494 precisa do protocolo do fabricante.
- **Decisão:** confirmar a origem do material nos protocolos.
  - [ ] `animal_derived_material` nos três.
  - [ ] Outra classificação, por método.

## 5. Soro animal (SFB) em métodos celulares

- **Métodos:** TG 460, 455, 456, 458, 432, 442D, 442E e GD 129.
- **Situação:** estão `NULL`. A regra 4 do ADR trata soro comercial como `animal_derived_material`.
- **O que os textos completos dizem (registrado como `culture_supplement` em `method_materials`):** exigem ou usam soro de origem animal a TG 460 (FCS/FBS a 10%), TG 432 (soro de bezerro recém-nascido a 10%), GD 129 (idem), TG 456 (Nu-Serum ou soro comparável), TG 455 e 458 (FBS e FBS tratado com carvão e dextrano), TG 491 (FBS a 10%), TG 494 (FBS a 5%), TG 490 (soro de cavalo), TG 442E (FBS no h-CLAT e FCS no U-SENS). A TG 442D usa soro no KeratinoSens (o tipo deve ser combinado com a autoridade, e há adaptação com soro humano), enquanto o α-Sens e o Epi2SensA não usam soro. O EpiSensA usa o kit LabCyte EPI-MODEL24, cujo meio de ensaio contém soro, segundo o manual do fabricante (espécie não informada; registrado em `method_materials`, migration 102). As TGs 473, 476 e 487 não mencionam soro.
- **MAT (Farmacopeia Brasileira):** as células são cultivadas com plasma do próprio doador, soro AB humano ou soro fetal bovino; só a terceira opção é de origem animal. Registrado em `method_materials`.
- **Pedidos dos usuários:** GD 129 "usa produto de origem animal" (#20), TG 432 "material derivado de animal" (#26) e TG 455 "misto ou variável" (#19).
- **Aplicado provisoriamente (migration 119):** assumido que o soro conta. Os métodos 8 (TG 460), 12 (TG 442E), 16 (TG 432), 22 (GD 129), 41 (TG 455), 43 (TG 456), 44 (TG 458) e 47 (TG 494) passaram de `NULL` para `animal_derived_material`. **A confirmar.**
- **Decisão:** definir se o uso de SFB nos protocolos conta.
  - [ ] Sim, e esses métodos passam a `animal_derived_material`.
  - [ ] Não, e o SFB não entra na classificação.
  - [ ] Caso a caso, conforme o protocolo permita ou não meio sem soro.

## 6. Possíveis `none`

- **Métodos:** rFC (método 56) e TG 493 (hrER), por usarem reagentes recombinantes. As TGs 439, 431, 492B e 493 também precisam ser verificadas.
- **Situação:** estão `NULL`, e a regra 7 diz que `NULL` não significa `none`.
- **O que os textos completos dizem:** as TGs 439 e 431 não citam soro nem componentes de origem animal (modelos de epiderme reconstruída com meio proprietário). A TG 493 usa receptor humano recombinante (resumo da TG). O capítulo <86> da USP (proposta) descreve o fator C recombinante (rFC) e o reagente em cascata recombinante (rCR) como "reagentes não derivados de animais", baseados na sequência gênica de fatores do caranguejo-ferradura. Isso sustenta `none` para o rFC (método 56), salvo insumos de outro tipo. Para os demais, a confirmação depende dos protocolos dos fabricantes.
- **Pedido dos usuários:** TG 431 "misto ou variável" (#21).
- **Aplicado provisoriamente (migration 119):** `none` no rFC (método 56) e no TG 493 (método 42), por usarem reagentes recombinantes (`animal_derived` falso). **A confirmar.** TG 492B (39), TG 435 (5) e TG 496 (49) continuam `NULL`.
- **Decisão:** confirmar a ausência de material animal e derivado (regra 3) em cada protocolo.
  - [ ] `none`, onde confirmado.
  - [ ] `NULL` até a confirmação.

## 7. Rationale dos 3Rs (`replacement_rationale`, `reduction_rationale`, `refinement_rationale`)

Já corrigido: erro de grafia no pt-br do TG 495 e o texto de replacement do DFA e do RT-PCR de raiva (migration 075); indicação de substituição total ou parcial em todos os `replacement_rationale` (migration 079); e a conferência com os textos completos das TGs 420, 425, 428, 429, 442A, 442B e 442C (migration 093).

O que os textos completos confirmam:
- **TG 429, 442A e 442B:** o LLNA e suas duas versões não radioativas oferecem, em relação aos testes em cobaias (TG 406), redução e "refinamento substancial (menos dor e sofrimento)". O argumento de refinamento é esse, não o de evitar isótopos radioativos, que o texto trata como segurança ocupacional. Os rationales foram reescritos: o 429 ganhou refinamento, o 442A ganhou redução e novo texto de refinamento, e o 442B teve o placeholder de redução preenchido e o texto de refinamento trocado.
- **TG 429:** o "até 40% menos animais" está no texto (LLNA reduzido, rLLNA).
- **TG 420:** "usa menos animais e causa menos sofrimento que os métodos tradicionais" (o "significativamente" não estava no texto e foi tirado).
- **TG 425:** o texto fala em minimizar o número de animais necessários. Não faz alegação de refinamento, então o placeholder de refinamento foi apagado e a redução foi escrita.
- **TG 442C, 442D e 442E:** os resultados podem não bastar como métodos isolados e devem ser usados em IATA ou em abordagens definidas (TG 497). Isso confirma "substituição parcial". Só o kDPRA (TG 442C) é descrito como substituto isolado de dados animais, e só para a subcategoria 1A.
- **TG 496, 439 e 467:** a TG 496 não é válida como substituto isolado do teste de olho em coelho; a TG 439 serve como teste autônomo ou parcial; e a TG 467 diz que o desafio de um único método in vitro é prever a categoria 2 do olho. Isso sustenta as classificações da migration 079.
- **TG 455, 456 e 458 (ensaios endócrinos in vitro):** o texto da TG 455 diz que os métodos são propostos "para triagem e priorização", com informação mecanística para uma abordagem de peso de evidência. A TG 440 (uterotrófico) e a TG 441 (Hershberger) são ensaios in vivo do nível 3 do Quadro Conceitual da OCDE, e os ensaios in vitro estão no nível 2. Nenhum dos textos diz que o ensaio in vitro substitui o in vivo. Isso enfraquece o rationale de substituição dos métodos 41, 42 (TG 493), 43 e a ausência de R no 44: eles complementam o teste in vivo (priorização), e não o substituem.
  - [ ] Manter "substituição parcial" nesses métodos.
  - [ ] Trocar por redução (priorização que evita testes in vivo desnecessários).
  - [ ] Retirar o R de substituição.
- **TG 439 (EpiSkin SIT):** o protocolo 131 do DB-ALM diz que o EpiSkin foi aprovado como substituição completa do teste de irritação cutânea em coelhos (Método B.46 da UE, 2009, e TG 439, 2010) e que o ESAC o endossou como substituto autônomo do teste de Draize para separar irritantes de não irritantes. Ele é o método de referência validado da TG 439 e não permite a categoria 3. Isso sustenta o "total" do JSON para o TG 439.
- **TG 430, 437 e 438:** os textos confirmam o material e a classificação parcial.
  - TG 430: discos de pele de ratos "humanamente mortos" de 28 a 30 dias (confirma `animals_killed_for_tissue`); identifica corrosivos e não corrosivos, mas "não permite a subcategorização" (confirma "parcial"); o texto compara com o teste em coelho da TG 404.
  - TG 437 e 438: "não podem ser usados sozinhos para substituir o teste de Draize in vivo", e são recomendados como etapa inicial de uma estratégia em etapas (Top-Down; TG 467 e 492B). Córneas bovinas de gado abatido para consumo humano ou outros usos comerciais, e olhos de galinhas de abatedouro "eliminando a necessidade de animais de laboratório" (confirma `slaughterhouse_byproduct`).
- **TG 421 e 422:**
  - TG 421: o texto diz que a diretriz "não é alternativa nem substitui" as TGs 414, 415, 416 ou 443, que gera informação limitada e que "não fornece evidência para afirmar ausência de efeitos". Pode servir como triagem ou como estudo de faixa de dose. O rationale de redução dizia que ela poderia reduzir a necessidade de estudos mais extensos "se não houver efeitos tóxicos", o que o texto contradiz. Reescrevi o rationale na migration 099.
  - TG 422: "pode servir como alternativa à realização de dois testes separados" (TG 407 e TG 421) e envolve menos animais, o que confirma a redução.
- **TG 236, 319A e 319B:** os textos não fazem alegação de 3Rs. A TG 236 descreve o teste com embriões de zebrafish e nota que a capacidade metabólica dos embriões nem sempre é igual à de peixes jovens ou adultos. As TGs 319A e 319B têm o objetivo de "melhorar previsões in silico de bioacumulação em peixes", e o RT-HEP e o RT-S9 podem ser comprados ou preparados em laboratório a partir de trutas (Anexo 2). O rationale do 236 (alternativa a testes com peixes jovens ou adultos) vem da literatura citada na TG 236 e não do texto da diretriz.
- **GD 280 (RT-HEP e RT-S9):** as previsões de BCF feitas com o clearance intrínseco in vitro servem como ferramenta de triagem para decidir se um estudo completo de BCF em peixes (TG 305) se justifica, "podem não substituir" os testes de bioacumulação in vivo e só seriam alternativa se o teste in vivo for inviável ou proibido. O rationale do 319B ("sem peixes vivos") foi trocado por esse texto, e o 319A recebeu o mesmo rationale de redução (migration 102).
- **TG 427:** é o comparador in vivo da TG 428; o rato é a espécie mais usada. O texto lista como desvantagens o uso de animais vivos e a necessidade de material radiomarcado.
- **TG 212:** o texto diz que "não substitui" a TG 210 e que serve como ponte ou triagem. É um teste in vivo com embriões e alevinos, o que combina com o método não ter R.
- **TG 493 e TG 495:** a TG 493 repete que os métodos são "propostos para triagem e priorização" (receptor humano ERα produzido em células de inseto infectadas por baculovírus, ligante radiomarcado). A TG 495 o descreve como ferramenta de triagem in chemico: um resultado negativo pode apoiar a decisão de que nenhuma avaliação adicional de fotossegurança é necessária, e resultados fotorreativos podem exigir dados adicionais. A TG 495 também chama a TG 432 de "método alternativo aos testes de fototoxicidade in vivo".
- **TG 497 e TG 467 (abordagens definidas):** pelo texto, combinações de métodos in vitro e in chemico substituem o teste animal de sensibilização cutânea e de olho "sem o uso de testes em animais". Elas não estão no catálogo (item 10).

Pendências:

- **Confirmar a classificação total ou parcial** da migration 079. Critério do plano e do glossário: total quando o método substitui sozinho o procedimento animal para o desfecho que cobre; parcial quando cobre só parte, é usado em estratégia em etapas ou ainda depende de tecido de animais.
  - Total: TG 431, 435, 432, 492B, MAT e rFC.
  - Total ou parcial: TG 439 (confirmado pelo texto da TG).
  - Parcial, ou total se a autoridade aceitar: GD 129.
  - Parcial: TG 430 (pele de rato), 437 e 438 (tecido de abatedouro), 460 (estratégia em etapas), 492, 491, 494 e 496 (não cobrem todas as categorias), 442C, 442D e 442E (confirmado pelos textos), 455, 493, 456 e 495 (triagem), 236 (embriões de peixe), LAL (só endotoxinas) e os quatro métodos de raiva (a inoculação em camundongos continua permitida como último recurso, art. 4º da Res. 75/2026).
  - [ ] Confirmar a lista.
  - [ ] Ajustar os métodos discordantes (informar quais).
- **Reavaliar os Rs dos demais métodos pelos critérios da seção 3 do plano** (substitui animais vivos, evita etapa, reduz número, reduz dor ou invasividade, e se mais de um R é justificável).
- **TG 430 (TER):** os usuários pedem trocar Replacement por Reduction e Refinement (#22). Hoje tem Replacement ("evitando o uso de animais vivos"), mas a nota da regulação diz "not full replacement" e o `animal_use` é `animals_killed_for_tissue`.
  - [ ] Manter Replacement (relativa).
  - [ ] Passar para Reduction.
- **TG 428:** não tem rationale, e o texto da TG não faz alegação de 3Rs. A nota da regulação diz "Uses excised skin — category = reduction, not replacement". O texto cita o equivalente in vivo (TG 427).
  - **Aplicado provisoriamente (migration 120):** `reduction_rationale` (en/pt) e `animal_procedures_avoided` com o estudo in vivo de absorção cutânea (TG 427, redução) no método 21. **A confirmar.**
  - [ ] Escrever um rationale de redução, com base na nota da regulação e no TG 427.
  - [ ] Deixar sem R.
- **Coluna que não bate com o texto:**
  - MAT (método 20): o próprio capítulo da Farmacopeia Brasileira (MG 5.5.2.7.1) diz que o MAT é o teste de escolha "em detrimento do teste de pirogênios em coelhos visando à redução de uso de animais". O texto do rationale reproduz essa redação, mas está em Replacement (total).
    - [ ] Manter em Replacement (total), com o texto reescrito para "substitui".
    - [ ] Passar para Reduction.
    - [ ] Manter os dois.
  - TG 496 (método 49): "reduzindo a dependência", mas está em Replacement.
- **Sem nenhum rationale (8 métodos):** TG 471, 473, 476, 487, 490, 428, 458 e 212. Decidir se é intencional (esses métodos ficam fora de todos os filtros de 3Rs) ou se falta preencher. O TG 428 foi preenchido provisoriamente (migration 120); os outros sete seguem sem R porque os textos não fazem alegação de 3Rs. Comparar com o TG 455/456 (com rationale) e o TG 319B (com rationale).

## 8. Status de validação

- **Já aplicado (migration 078):** `recognized` foi adicionado e `not_evaluated` foi removido. O vocabulário atual é `recognized`, `under_validation`, `validated`, `partially_validated`, `not_validated` e `unclear`. Nenhum método usava `not_evaluated`. Os 47 métodos continuam `validated`.
- **Plano (`Revisao.md`):** Validado (aceitação regulatória internacional, como OECD, farmacopeia ou OMS), Reconhecido (específico do Brasil), Em processo de validação, Descrito na literatura científica e Descrito na literatura cinzenta.
- **Decisões:**
  - [ ] Padrão de métodos novos: o padrão passou a `unclear`, porque `not_evaluated` saiu. Manter, ou exigir que o campo seja preenchido?
  - [ ] Quais dos 47 métodos passam a `recognized`. Os usuários pedem "Reconhecido" para 11 (registros #6, #10 a #14 e #22 a #26 do feedback): dRIT, ICE, TG 442C, RT-PCR, DFA, RTCIT, TER, TG 435, TG 439, TG 460 e TG 432. Todos os 47 têm reconhecimento por uma RN, então a regra precisa ser definida: quem tem aceitação internacional (OECD, farmacopeia) fica `validated`, ou o reconhecimento pelo Brasil prevalece?
  - [ ] Acrescentar "Descrito na literatura científica" e "Descrito na literatura cinzenta" ao vocabulário.
  - [ ] Manter `partially_validated`, `not_validated` e `unclear`, que o plano não lista.

## 9. Valor `in_data` em `test_system`

- **Situação:** `in_data` foi aberto na CHECK constraint, no código e na interface (migration 077), com o rótulo "In data", mas sem definição e sem nenhum método usando. O `hybrid` foi removido (migration 078).
- **Decisão:**
  - [ ] Escrever a definição no glossário (en e pt) e nas regras de curadoria do `test_system`.
  - [ ] Dizer quais métodos devem usar o valor.

- [ ] **`unclear` em `test_system`:** o plano lista 6 categorias (in vivo, in silico, in vitro, ex vivo, in data, in chemico) e o banco aceita também `unclear`. Nenhum método usa. Manter ou remover?

## 10. Mapeamento OHT

O OHT (OECD Harmonised Templates) está ligado aos métodos pelos endpoints (`methods.endpoints` → `endpoints.external_oht_codes`). Os códigos que faltavam nos endpoints foram corrigidos (migrations 071 a 073). Restam diferenças entre o que cada endpoint herda e o que o OHT lista para cada TG.

- **Decisão: de onde vem o código OHT de um método.**
  - [ ] Do endpoint (como hoje): o método herda todos os templates do endpoint.
  - [ ] Do método: um mapeamento próprio, derivado da lista de TGs de cada template OHT.
- **Diferenças que o mapeamento por método resolveria:**
  - TG 420, 423 e 425: o OHT lista só o template 60 (oral), e o endpoint herda também 61, 62 e 63 (inalatória, dérmica e outras vias).
  - TG 471, 473, 476, 487 e 490: o OHT lista 70 (in vitro), e os endpoints herdam também 71 (in vivo).
  - TG 212: o OHT lista só 42, e o endpoint herda 41 e 42. TG 236: o OHT lista só 41.
  - TG 421: o OHT lista só 73, e os endpoints herdam também 74.
  - TG 422: o OHT lista 67, 68, 69-1, 73 e 76; os endpoints dão também 69-2 e 74, e faltava o 76.
  - TG 496 e GD 129: nenhuma das duas aparece em template OHT. A TG 496 cai em 65 pelo endpoint, e a GD 129 cai em 60 a 63 e 201.
- **Códigos genéricos 78 e 201:** foram removidos dos endpoints de fototoxicidade, fotorreatividade, estrogênica, androgênica e esteroidogênese. Continuam em 3 (Atividades biológicas), 3.1 (Atividade endócrina), 3.1.3 (Tireoide), 2.6.2 e 2.6.3.
  - [ ] Manter nesses endpoints.
  - [ ] Remover também (3.1 e 3.1.3 ficariam sem nenhum código).
- **Nomenclatura do 497:** o arquivo adicionado se chama "GD 497", mas a capa diz "Guideline No. 497 Defined Approaches on Skin Sensitisation" (série de Diretrizes de Teste, seção 4), e as TGs 442B e 442C o citam como "TG 497". Neste documento usei "TG 497"; ajustar se o catálogo for tratá-lo como GD.
- **Método candidato novo:** o reagente em cascata recombinante (rCR), descrito no capítulo <86> da USP junto com o rFC, não está no catálogo.
  - [ ] Incluir o rCR no catálogo.
  - [ ] Tratar como variante do rFC.
- **Candidatos com texto completo agora na pasta:**
  - TG 249 (RTgill-W1): linhagem de brânquia de truta arco-íris, uma das espécies da TG 203; a exposição usa meio sem componentes animais (L-15/ex), mas a cultura da linhagem usa meio L-15 com 10% de FBS.
  - TG 444A (IL-2 Luc e IL-2 Luc LTT): células 2H4, derivadas de Jurkat (linfócitos T humanos); o texto diz que a capacidade preditiva não é satisfatória isoladamente e que o ensaio serve em combinação com outros.
  - TG 498 (fototoxicidade em epiderme humana reconstruída): modelo feito de queratinócitos humanos; vira candidato também a comparador de TG 432 e 495.
- **TGs do OHT que não estão no catálogo** e são in vitro ou alternativas: TG 249 (peixe, linhagem celular), TG 467 (abordagens definidas para olho), TG 497 (abordagens definidas para sensibilização cutânea), TG 498 (fototoxicidade) e TG 444A (imunotoxicidade). A lista vem do meu conhecimento do catálogo da OECD e precisa ser conferida.
  - [ ] Incluir no catálogo.
  - [ ] Fora do escopo.

## 11. Confirmações e verificações

- [x] **Referência da RN 32 (feedback #11):** o pedido diz "Incluir RN 32 do CONCEA" para o TG 442C. A RN 32 existe (6/9/2016, DOU de 8/9/2016), mas trata das diretrizes de integridade e boas práticas para produção, manutenção e uso de animais em ensino e pesquisa, e não reconhece métodos alternativos (fonte: resumo de terceiros, ABMES; a página oficial do CONCEA exigiu verificação anti-robô e não pôde ser lida). A resolução que reconhece o TG 442C é a RN 31/2016 (18/8/2016), que já está no banco; a "RN 32" é provavelmente digitação. Falta só confirmar com quem fez o pedido.
  - [ ] Confirmar com o usuário do feedback #11.
- [ ] **Pergunta dos usuários sobre TG ou GD (feedback #15):** a RN 18 chama o GD 129 de "TG 129". Como o título foi mantido, a pergunta fica sem efeito. Responder aos usuários.
- [ ] **Exibição das referências das RNs na interface:** todos os métodos têm uma regulação do Brasil com o documento da RN, mas não verifiquei se a interface mostra isso (feedback #17).
- [ ] **Já lidos e incorporados:** o capítulo 3.1.19 de raiva do Manual da WOAH (2023), o volume I da Farmacopeia Brasileira, 7ª edição, em texto (capítulos do MAT, do teste de pirogênios em coelhos e do LAL; o capítulo do LAL, lido antes por OCR no PDF escaneado, foi confirmado no texto) e o capítulo <86> da USP sobre reagentes recombinantes (registrado em `documents`, migration 097). Da Farmacopeia Europeia, os textos dos capítulos 2.6.30 (MAT, ed. 11.5, que inclui o 2.6.40, MAT para vacinas com componentes pirogênicos próprios) e 2.6.32 (rFC, ed. 10.3) estão na pasta `docs` e conferem com os registros de `method_materials` dos métodos 20 e 56: o MAT usa células humanas (sangue total, PBMC ou linhagem monocítica) em meio com plasma do próprio doador, soro AB humano ou soro fetal bovino, e o rFC é baseado na sequência gênica do caranguejo-ferradura, sem material animal declarado. Os capítulos 2.6.8 (Pyrogens) e 2.6.14 (Bacterial endotoxins) não estão na pasta; só os títulos são usados (migration 103), e nenhuma decisão depende do texto.
- [ ] **USP <86> e o rFC:** o capítulo da USP é uma proposta de novo capítulo (ainda não vinculado a monografia), descreve o teste como alternativo (sujeito às Notas Gerais 6.30) e diz que autoridades podem exigir estudo comparativo com o capítulo <85>. Decidir se ele entra como segunda fonte ou como evidência de validação do rFC (`validation_doc_id`), sabendo que ele não é uma aceitação em vigor; a evidência de aceitação internacional é a Farmacopeia Europeia.
- [ ] **Textos completos:** todas as TGs do catálogo e as candidatas (TGs 249, 444A e 498), a TG 427, o GD 280, o manual do LabCyte EPI-MODEL e o folheto do EpiSensA estão na pasta. Continuam faltando: os protocolos dos demais modelos reconstruídos (EpiDerm SIT e SCT, epiCS, Skin+, KeraSkin, EpiOcular, SkinEthic HCE, LabCyte CORNEA-MODEL24 e MCTT HCE); a origem dos componentes das TGs 435, 494 e 496; a ficha do conjugado de anticorpos do DFA e do dRIT.
- [ ] **Migrations 068 a 102, as mudanças de código e de interface (vocabulários de `test_system`, `validation_status`, `regulatory_status` e `applications`) e os documentos desta pasta** ainda não foram commitados nem testados na interface.
- [x] **Outros vocabulários fixos no código:** `applications`, vias (`routes`), espécies (`species`) e endpoints (`endpoints`) são lidos das tabelas no backend (`services/vocabulary.py`); no frontend, aplicações, vias e espécies vêm da API (`/vocabularies/species` é novo). Ficam fixos só os marcadores `in_vitro` e `other` de espécie. Pendente: a lista de endpoints do formulário do frontend (16 categorias gerais, `ENDPOINT_CATEGORIES`) e o texto dos prompts de extração (sinônimos de via e espécie).

## 12. Nomes dos métodos (pt-br e en-us) e TG 442D e 442E

O plano diz: em inglês, manter o nome como está no documento oficial (OECD, farmacopeias); em português, usar o nome como está na RN do CONCEA; para métodos ainda não reconhecidos, tradução livre. Hoje todos os 47 métodos têm RN, então não há caso de tradução livre.

- **Português:** em 22 métodos o nome é diferente do texto da RN (Apêndice A.2). Isso reverte a decisão anterior de manter os títulos.
  - [ ] Manter os títulos atuais.
  - [ ] Usar o texto da RN nos 22 métodos.
  - [ ] Com o prefixo "Método OECD TG nnn - " (como nos pedidos dos usuários), ou só o texto depois do hífen.
- **Inglês:** 11 dos 15 métodos com nome diferente do título do documento-fonte foram corrigidos (migrations 091, 095 e 103); os 4 restantes estão no Apêndice A.3.
- **LAL em português:** o capítulo da Farmacopeia Brasileira (MG 5.5.2.7.3-02) se chama "Teste de endotoxinas bacterianas" (plural), e a RN 31/2016 escreve "Teste de Endotoxina Bacteriana (Farmacopeia Brasileira)" (singular). O nome em português do método usa a RN, como pede o plano.
  - [ ] Manter a redação da RN (singular).
  - [ ] Usar o título da Farmacopeia (plural).
  - [ ] Trocar pelos títulos oficiais.
  - [ ] Manter os nomes atuais nos casos em que a diferença é só de forma.
  - [ ] Conferir o nome oficial dos métodos de farmacopeia e de raiva, que dependem de documentos que não estão na pasta.
- **Regra para métodos novos:** o plano diz que, para métodos ainda não reconhecidos, o nome em português é tradução livre. O prompt de extração de métodos (`method_draft_extraction.py`) ainda não tem essa regra de nomes (inglês oficial; português igual à RN quando reconhecido, tradução livre caso contrário).
  - [ ] Acrescentar a regra ao prompt.
  - [ ] Manter sem regra.
- **TG 442D e TG 442E (confirmação):** o título oficial das duas é o mesmo, "In Vitro Skin Sensitisation". Os subtítulos que acrescentei (migration 069) são paráfrases minhas, e "Evento-Chave" (en: "Key Event") é uma tradução minha.
  - Subtítulo oficial do 442D: "Assays addressing the Adverse Outcome Pathway Key Event on Keratinocyte activation".
  - Subtítulo oficial do 442E: "In Vitro Skin Sensitisation assays addressing the Key Event on activation of dendritic cells on the Adverse Outcome Pathway for Skin Sensitisation".
  - Em pt-br, o texto da RN é "Sensibilização cutânea in vitro" para as duas (a RN 56/2022 acrescenta uma descrição longa ao 442E), então o texto da RN sozinho voltaria a deixar os nomes iguais.
  - [ ] Manter os subtítulos atuais.
  - [ ] Usar os subtítulos oficiais.
  - [ ] Diferenciar só pela sigla (TG 442D e TG 442E).
  - [ ] Confirmar a tradução "Evento-Chave" ou indicar o termo da plataforma.

## 13. Campos exigidos pelo plano

Os campos foram criados nas migrations 081 a 085. Falta a curadoria preencher e decidir.

- **Data limite para a substituição (`regulations`):** `published_date`, `effective_date`, `replacement_term_years` e `replacement_deadline` (calculada). Preenchidas nas linhas do Brasil a partir dos textos das RNs (RN 56/2022: vigência em 01/11/2022, prazo até 01/11/2027). A RN 45/2019 foi assinada em 22/10/2019 e publicada em 25/10/2019 (migration 087 corrigiu as datas e o prazo).
  - [x] Datas de publicação conferidas no Diário Oficial: RN 18/2014 em 25/09/2014 (Seção I, p. 9) e RN 31/2016 em 19/08/2016 (p. 4; o PDF do CONCEA indica Seção I, e a confirmação recebida indica Seção II, o que não altera a data); RN 45/2019 em 25/10/2019; RN 56/2022 em 07/10/2022; Res. 75, 76 e 77/2026 nas datas do cabeçalho do DOU. A seção e a página não são guardadas no banco.
  - [ ] Decidir se as linhas da OECD ficam sem datas (hoje ficam).
  - [ ] Decidir como mostrar o prazo na interface (as RNs 18 e 31 já venceram).
- **Material ou sistema biológico (`method_materials`):** 71 linhas, uma ou mais para cada um dos 47 métodos. Cada linha tem a fonte em `notes` (resumo ou texto da TG, GD 129, descrição do método ou RN). As linhas marcadas "confirm" ou "to confirm" dependem do protocolo completo. Os textos completos de 20 TGs (itens 1, 2, 4, 5 e 6) já foram lidos e alimentaram a migration 092: S9 dos cinco testes de genotoxicidade, 11 linhas de soro e suplementos, e as matrizes das TGs 435, 494 e 496.
  - As espécies das linhagens estão confirmadas: U937 (humana) e Neuro-2a/N2a (camundongo) pelo catálogo da ATCC (CRL-1593.2 e CCL-131, migration 100), TK6 (humana) e os queratinócitos do KeratinoSens e do LuSens (humanos) pelos textos das TGs. A linhagem do α-Sens também é derivada de queratinócitos humanos (TG 442D).
  - Os textos confirmam que o S9 dos cinco testes de genotoxicidade vem de fígado de roedores (geralmente ratos) tratados com indutores. O que falta é a regra de classificação (item 1).
  - [ ] Origem do colágeno (TG 494) e das proteínas da barreira (TG 435) e do reagente (TG 496): os textos não dizem, e os registros ficaram com `animal_derived` vazio.
  - [ ] Regra de `animal_derived`: hoje é verdadeiro quando o método usa material tirado de animais (tecido, organismo, S9, lisado) e fica vazio para linhagens celulares de origem animal (MDCK, SIRC, 3T3). Confirmar a regra.
  - [ ] Nome em pt-br de zebrafish ("Paulistinha (zebrafish)"): confirmar, ou usar "Peixe-zebra".
- **Espécie (`species`):** 13 espécies, incluindo as bactérias dos testes de mutação reversa (*Salmonella typhimurium* e *Escherichia coli*).
  - [ ] Acrescentar as espécies que faltarem (por exemplo hamster, se as linhagens CHO e V79 forem registradas).
  - [ ] Decidir se a extração do protocolo passa a ler as espécies desta tabela, em vez da lista fixa.
- **Procedimento animal evitado (`methods.animal_procedures_avoided`):** preenchido em 36 métodos. Os testes in vivo convencionais (TG 404, 405, 406, 429, 401 e 203) vêm da tabela OHT e dos textos das TGs (por exemplo, TG 429, 442A e 442B comparam-se aos testes em cobaias da TG 406). As espécies dos testes convencionais são as das TGs (coelho, cobaia, camundongo e rato) e precisam de confirmação.
  - Faltam 3 métodos que têm rationale e nenhum procedimento: TG 455, 493 e 456. Os textos das TGs 432, 421, 422 e 495 trouxeram o comparador (testes de fototoxicidade in vivo, estudos reprodutivos mais extensos, estudos separados das TGs 407 e 421) e eles foram preenchidos na migration 099. Os textos completos dos comparadores convencionais (TG 404, 405, 406, 440, 441, 203, 305) foram lidos: confirmam as espécies (coelho albino nas TGs 404 e 405, cobaia na TG 406, rato nas TGs 440 e 441, com camundongo também aceito na 440) e que a TG 406 só deve ser usada "como último recurso" por razões de bem-estar. A TG 401 foi retirada pela OCDE em 17/12/2002 (o arquivo é só o aviso), e isso foi anotado nos procedimentos que a citam. Nenhum texto liga os 3 métodos restantes a um comparador, então eles ficaram em branco. O TG 319A e o TG 319B foram preenchidos com a GD 280 (migration 102).
  - [ ] Preencher esses 3 com o comparador que a curadoria indicar (as TGs 440 e 441 para os endócrinos, se a decisão do item 7 mantiver o R).
  - [ ] Confirmar o `extent` do TG 439: o texto da TG confirma que serve como teste autônomo ou parcial, e o JSON registra como total.
  - [ ] Decidir se `replacement_rationale` passa a ser derivado deste campo ou continua separado.
- **Perguntas de controle do plano (10 perguntas antes de aprovar um método):** não há onde registrar as respostas, o revisor e a data.
  - [ ] Criar um campo `review_checklist` (JSON) com as 10 respostas, mais revisor e data da revisão.
  - [ ] Registrar fora do banco (documento de revisão).
- **Marca de revisão (`methods.review_status`):** coluna criada (`not_reviewed`, `in_review`, `reviewed`), com todos os 47 métodos em `not_reviewed`, inclusive o GD 129, que está ativo.
  - [ ] Definir quem pode mudar o estado e como a revisão é registrada (revisor e data não foram criados).
  - [ ] Decidir se só métodos `reviewed` podem ficar ativos.
  - [ ] Decidir o que fazer com o GD 129, ativo sem revisão.
- **Referência:** o plano pede incluir as RNs. Hoje `source_doc_id` aponta para o documento da OECD (ou farmacopeia ou WOAH), e as RNs só aparecem pelas regulações.
  - [ ] Verificar na interface e decidir se a RN entra na referência.

## 14. Finalidade e contexto de aplicação

Já aplicado (migration 080 e mudanças no código): ver "Decididos e já aplicados" no topo. O plano lista 8 valores (pesquisa básica, translacional/aplicada, uso regulatório, produção de rotina, ensino/treinamento profissional, proteção ambiental, preservação de espécies e teste diagnóstico). O banco tem esses 8 mais "Investigação forense" e "Outro".

- [ ] **Confirmar o rótulo "Educação e treinamento"** (padronizado em pt-br na migration 080; o plano usa "ensino/treinamento profissional" e a tabela usava "Ensino e treinamento").
  - [ ] "Educação e treinamento".
  - [ ] "Ensino e treinamento".
  - [ ] "Ensino/treinamento profissional".
- [ ] **Confirmar as duas categorias acrescentadas aos métodos** (migration 080): "Produção de rotina" para MAT, LAL e rFC (controle de qualidade e liberação de lotes de injetáveis) e "Proteção do meio ambiente natural" para TG 212, TG 236, TG 319A e TG 319B (ecotoxicidade e bioacumulação em peixes).
- [ ] **Pesquisa:** nenhum método tem "Pesquisa básica" nem "Pesquisa translacional e aplicada". Hoje 43 métodos têm só "Uso regulatório" e 4 só "Teste diagnóstico". Como a extração usa "Pesquisa básica" quando o propósito não está claro, um protocolo assim não recebe o bônus de aplicação em nenhum dos 43 métodos. Quais métodos devem incluir pesquisa?
  - [ ] Os ensaios mecanísticos e de triagem (TG 455, 456, 458, 493, 495, 442C, 442D e 442E).
  - [ ] Todos os métodos in vitro e in chemico.
  - [ ] Nenhum (a aplicação descreve só o uso regulatório ou diagnóstico).
  - [ ] Mudar o padrão da extração, hoje "Pesquisa básica" quando o propósito não está claro.
- [ ] **Questões definicionais:**
  - "Pesquisa translacional e aplicada" inclui "diagnóstico" na definição, e existe "Teste diagnóstico" à parte. Os métodos de raiva ficam só em "Teste diagnóstico".
    - [ ] Tirar "diagnóstico" da definição de pesquisa translacional.
    - [ ] Manter e aceitar a sobreposição.
  - "Uso regulatório" ("avaliar qualidade, segurança, eficácia ou efeitos ambientais") se sobrepõe a "Produção de rotina" ("controle de qualidade, liberação de lotes") nos ensaios de farmacopeia, e a "Proteção do meio ambiente natural" nos ensaios ecotoxicológicos. MAT, LAL, rFC e os de peixe agora têm as duas categorias.
    - [ ] Manter as duas categorias nesses métodos.
    - [ ] Ajustar as definições para separar uso regulatório do controle de qualidade e do ambiental.
  - [ ] "Teste diagnóstico" não está na lista do plano como subtipo de outra categoria: confirmar que fica como categoria própria.
- [ ] **Remover "Investigação forense" e "Outro"**, que o plano não lista (nenhum método usa).
- [x] **Remover as aplicações aceitas pela extração só como legado** (`general`, `pharma`, `cosmetics`, `chemical-safety`, `education`): os apelidos fixos foram retirados do backend e do frontend. Esses valores agora não existem na tabela `applications` e, no backend, caem no padrão `basic-research`. O nome antigo do campo, `study_domain` (e `study_domain_evidence` e `study_domain_confidence`), também deixou de ser aceito nas respostas da extração e no frontend.

## 15. Endpoints

Já aplicado (migration 078), mantendo os gerais:
- MAT (método 20): acrescentado "Pirogenicidade" (5.1.1); ficou com "Contaminação pirogênica", "Pirogenicidade" e "Pirógenos não endotoxínicos".
- TG 487 (método 19): acrescentado "Mutagenicidade" (2.4.1.1); ficou com "Genotoxicidade" e "Mutagenicidade", como o TG 473.

Para confirmar:
- [ ] "Mutagenicidade" no TG 487: o micronúcleo detecta dano cromossômico. Se a curadoria considerar que o endpoint específico é outro, ajustar.
- [ ] O LAL (método 38) já tinha "Endotoxinas bacterianas" além do geral, e o rFC só tem o específico. Sem mudança.

## 16. Status regulatório `recognized`

**Decidido e aplicado (migrations 111 e 128):** as 47 regulações do Brasil (reconhecimento por RN do CONCEA) são `recognized`; as 39 TGs da OECD são `adopted` e o GD 129 é `published`. `adopted` e `published` foram acrescentados a `regulations.regulatory_status`, aos rótulos (`enum_terms`), aos modelos e aos prompts de extração. O valor `approved` continua permitido, mas nenhuma regulação o usa. O plano diz que "validated", "accepted", "recognized", "recommended" e "approved" não são sinônimos.
- [x] Passar as regulações do Brasil para `recognized` e as da OECD para `adopted` (TGs) e `published` (GD).

---

## 17. TG 319A e 319B: substituição ou redução

- **Métodos:** 54 (TG 319A, hepatócitos criopreservados de truta) e 55 (TG 319B, fração S9 de fígado de truta).
- **Situação:** os dois estão `animals_killed_for_tissue`, com `reduction_rationale` e sem `replacement_rationale`. O procedimento evitado ("estudo de bioconcentração in vivo em peixes") está com `r_type: reduction`. A justificativa vem do GD 280: as previsões de BCF a partir do clearance in vitro servem para decidir se um estudo completo de BCF em peixes é necessário e podem não o substituir; podem ser uma alternativa quando o teste in vivo não for viável.
- **Dúvida:** o procedimento deveria constar também como substituição parcial?
- **Decisão:**
  - [ ] Manter como redução.
  - [ ] Marcar também como substituição parcial (e acrescentar `replacement_rationale`).

## 18. Valor `embryos_and_larvae` em `animal_use`

- **Métodos:** 51 (TG 212, embrião e alevino com saco vitelino) e 53 (TG 236, embrião de peixe, 96 h).
- **Situação:** os dois estavam `live_animals`. O TG 236 diz na própria justificativa que usa embriões como substituição parcial de testes em peixes juvenis ou adultos. O TG 212 vai até o fim do estágio de saco vitelino, mais tardio que o embrião do TG 236.
- **Aplicado provisoriamente (migration 118):** novo valor `embryos_and_larvae` (CHECK, `enum_terms`, ADR-026, glossário e prompt) e os métodos 51 e 53 passaram para ele. **A confirmar.**
- **Decisão:**
  - [ ] Manter `embryos_and_larvae` nos dois.
  - [ ] Manter só no TG 236 e voltar o TG 212 para `live_animals`.
  - [ ] Voltar os dois para `live_animals`.

---

## Apêndice A. Comparativo dos títulos dos métodos com as resoluções do CONCEA

Quote = item da alínea na resolução brasileira (sem o cabeçalho do desfecho). Estado do banco após as migrations 068 a 070 (os títulos não mudaram depois). Todas as linhas estão com "Manter", por decisão de manter os títulos atuais.

### A.1 Títulos semelhantes ao quote (25)

O título em pt-br corresponde à redação da resolução (diferenças só de pontuação, ordem ou capitalização).

| ID | Ref. | Quote (resolução) | Título pt-br | Título en-us | Recomendação | Justificativa |
|---|---|---|---|---|---|---|
| 4 | TG 430 | a) Método OECD TG 430 - Corrosão dérmica in vitro: Teste de Resistência Elétrica Transcutânea; | Teste de Resistência Elétrica Transcutânea (TER) | Transcutaneous Electrical Resistance (TER) Test | Manter | Título e quote equivalentes. |
| 6 | TG 437 | a) Método OECD TG 437 - Teste de Permeabilidade e Opacidade de Córnea Bovina; | Teste de Permeabilidade e Opacidade de Córnea Bovina (BCOP) | Bovine Corneal Opacity and Permeability (BCOP) Assay | Manter | Nome alinhado à redação da resolução. |
| 7 | TG 438 | b) Método OECD TG 438 - Teste de Olho Isolado de Galinha; e | Teste de Olho Isolado de Galinha | Isolated Chicken Eye Test Method | Manter | Nome alinhado à redação da resolução. |
| 10 | TG 442C | a) Método OECD TG 442C - Sensibilização cutânea in chemico; | Sensibilização Cutânea In Chemico | In Chemico Skin Sensitisation | Manter | Título e quote equivalentes. |
| 11 | TG 442D | b) Método OECD TG 442D - Sensibilização cutânea in vitro; | Sensibilização Cutânea In Vitro: Evento-Chave de Ativação de Queratinócitos | In Vitro Skin Sensitisation: Key Event on Keratinocyte Activation | Manter | Início do quote igual ao de 442E; subtítulo do PDF para diferenciar. |
| 12 | TG 442E | a) Método OECD TG 442E - Sensibilização cutânea in vitro: ensaios de sensibilização cutânea in vitro abordando o evento chave na ativação de células dendríticas no Caminho da Resposta Adversa (AOP) para sensibilização cutânea. | Sensibilização Cutânea In Vitro: Evento-Chave de Ativação de Células Dendríticas | In Vitro Skin Sensitisation: Key Event on Dendritic Cell Activation | Manter | Quote é descrição longa e começa igual ao de 442D; subtítulo do PDF. |
| 13 | TG 429 | a) Método OECD TG 429 - Sensibilização Cutânea: Ensaio do Linfonodo Local; e | Ensaio do Linfonodo Local (LLNA) | Local Lymph Node Assay (LLNA) | Manter | Título e quote equivalentes. |
| 16 | TG 432 | a) Método OECD TG 432 - Teste de Fototoxicidade in vitro 3T3 NRU. | Teste de Fototoxicidade in vitro 3T3 NRU | In Vitro 3T3 NRU Phototoxicity Test | Manter | Título e quote equivalentes. |
| 17 | TG 471 | a) Método OECD TG 471 - Teste de mutação bacteriana reversa. | Teste de Mutação Bacteriana Reversa | Bacterial Reverse Mutation Test | Manter | Nome alinhado à redação da resolução. |
| 18 | TG 476 | c) Método OECD TG 476 - Testes in vitro de mutação gênica de células de mamífero usando os gens Hprt and xprt. | Testes In Vitro de Mutação Gênica de Células de Mamífero Usando os Genes Hprt e xprt | In Vitro Mammalian Cell Gene Mutation Tests using the Hprt and xprt genes | Manter | Alinhado ao quote, sem o erro "gens". |
| 19 | TG 487 | a) Método OECD TG 487 - Teste do Micronúcleo em Célula de Mamífero in vitro. | Teste do Micronúcleo em Célula de Mamífero In Vitro | In Vitro Mammalian Cell Micronucleus Test | Manter | Nome alinhado à redação da resolução. |
| 20 | - | o Conselho Nacional de Controle de Experimentação Animal reconhece o método alternativo Teste de Ativação de Monócitos para avaliação da contaminação pirogênica em produtos injetáveis. | Teste de Ativação de Monócitos (MAT) | Monocyte Activation Test (MAT) | Manter | Título e quote equivalentes. |
| 21 | TG 428 | a) Método OECD TG 428 - Absorção Cutânea método in vitro. | Absorção Cutânea: Método In Vitro | Skin Absorption: In Vitro Method | Manter | Nome alinhado à redação da resolução. |
| 23 | TG 420 | a) Método OECD TG 420 - Toxicidade Aguda Oral – Procedimento de Doses Fixas; | Toxicidade Aguda Oral – Procedimento de Doses Fixas | Acute Oral Toxicity - Fixed Dose Procedure | Manter | Nome alinhado à redação da resolução. |
| 24 | TG 423 | b) Método OECD TG 423 - Toxicidade Aguda Oral – Classe Tóxica Aguda; | Toxicidade Aguda Oral – Classe Tóxica Aguda | Acute Oral Toxicity – Acute Toxic Class Method | Manter | Nome alinhado à redação da resolução. |
| 25 | TG 425 | c) Método OECD TG 425 - Toxicidade Aguda Oral – procedimento "Up and Down"; e | Toxicidade Aguda Oral – Procedimento Up and Down | Acute Oral Toxicity: Up-and-Down Procedure | Manter | Nome alinhado à redação da resolução. |
| 36 | TG 421 | a) Método OECD TG 421 - Teste de triagem para toxicidade reprodutiva e do desenvolvimento; | Teste de Triagem para Toxicidade Reprodutiva e do Desenvolvimento | Reproduction/Developmental Toxicity Screening Test | Manter | Nome alinhado à redação da resolução. |
| 38 | - | a) Teste de Endotoxina Bacteriana (Farmacopeia Brasileira). | Teste de Endotoxina Bacteriana (LAL) | Bacterial Endotoxins Test (LAL) | Manter | Nome alinhado à redação da resolução. |
| 43 | TG 456 | a) Método OECD TG 456 - Ensaio de Esteroidogênese H295R. | Ensaio de Esteroidogênese H295R | H295R Steroidogenesis Assay | Manter | Título e quote equivalentes. |
| 45 | TG 473 | b) Método OECD TG 473 - Teste in vitro de aberração cromossômica de mamíferos. | Teste In Vitro de Aberração Cromossômica de Mamíferos | In Vitro Mammalian Chromosomal Aberration Test | Manter | Nome alinhado à redação da resolução. |
| 46 | TG 490 | d) Método OECD TG 490 - Testes in vitro de mutação gênica em células de mamífero usando gen Timidinaquinase. | Testes In Vitro de Mutação Gênica em Células de Mamífero Usando o Gene da Timidina Quinase | In Vitro Mammalian Cell Gene Mutation Tests Using the Thymidine Kinase Gene | Manter | Alinhado ao quote, sem o erro "Timidinaquinase". |
| 50 | TG 495 | a) OECD TG 495 - Ensaio de fotorreatividade por Ros (Espécies oxigênio reativas). | Ensaio de Espécies Reativas de Oxigênio (ROS) para Fotorreatividade | Ros (Reactive Oxygen Species) Assay for Photoreactivity | Manter | Grafia corrigida (migration 070). |
| 53 | TG 236 | b) Método OECD TG 236 - Toxicidade aguda em embrião de peixe (FET). | Toxicidade Aguda em Embrião de Peixe (FET) | Fish Embryo Acute Toxicity (FET) Test | Manter | Nome alinhado à redação da resolução. |
| 54 | TG 319A | c) Método OECD TG 319-A - Determinação do "clearance" intrínseco "in vitro" usando hepatócitos criopreservados de Truta Arco-Íris (RT-HEP). | Determinação do Clearance Intrínseco In Vitro Usando Hepatócitos Criopreservados de Truta Arco-Íris (RT-HEP) | Determination of in vitro intrinsic clearance using cryopreserved rainbow trout hepatocytes (RT-HEP) | Manter | "Clearance" padronizado nos dois (migration 070). |
| 55 | TG 319B | d) Método OECD TG 319-B - Determinação do "clearance" intrínseco "in vitro" usando fração sub-celular S-9 de Truta Arco-Íris (RT-S9). | Determinação do Clearance Intrínseco In Vitro Utilizando Fração Subcelular S9 de Fígado de Truta Arco-Íris (RT-S9) | Determination of in vitro intrinsic clearance using rainbow trout liver S9 sub-cellular fraction (RT-S9) | Manter | "Clearance" padronizado nos dois (migration 070). |

### A.2 Títulos diferentes do quote (22)

O quote da resolução é mais curto, mais amplo, compartilhado entre métodos ou usa outro termo; o título atual foi mantido.

| ID | Ref. | Quote (resolução) | Título pt-br | Título en-us | Recomendação | Justificativa |
|---|---|---|---|---|---|---|
| 1 | TG 439 | d) Método OECD TG 439 - Teste de irritação Cutânea in vitro. | Irritação Cutânea In Vitro: Método de Teste de Epiderme Humana Reconstruída | In Vitro Skin Irritation: Reconstructed Human Epidermis Test Method | Manter | Quote perde "epiderme humana reconstruída". |
| 3 | TG 431 | b) Método OECD TG 431 - Corrosão dérmica in vitro: Teste da Epiderme Humana Reconstituída; | Corrosão cutânea in vitro: método de teste de epiderme humana reconstruída (RHE) | In vitro skin corrosion: reconstructed human epidermis (RHE) test method | Manter | Resolução diz "dérmica" e "Reconstituída"; padrão do projeto é "cutânea" / "Reconstruída". |
| 5 | TG 435 | c) Método OECD TG 435 - Teste de Barreira de Membrana in vitro; e | Método de Teste de Barreira de Membrana in Vitro para Corrosão Cutânea | In Vitro Membrane Barrier Test Method for Skin Corrosion | Manter | Quote não traz "para corrosão cutânea". |
| 8 | TG 460 | c) Método OECD TG 460 - Teste de Permeação de Fluoresceína. | Método de teste de vazamento de fluoresceína para identificação de corrosivos oculares e irritantes graves | Fluorescein Leakage Test Method for Identifying Ocular Corrosives and Severe Irritants | Manter | Resolução diz "Permeação"; a TG diz "vazamento". Nome traz a finalidade. |
| 9 | TG 492 | b) Método OECD TG 492 - Epitélio corneal humano reconstruído; | Método de ensaio de Epitélio Corneo-símile Humano Reconstituído (RhCE) para identificação de produtos químicos que não requerem classificação e rotulagem para irritação ocular ou dano ocular grave | Reconstructed human Cornea-like Epithelium (RhCE) test method for identifying chemicals not requiring classification and labelling for eye irritation or serious eye damage | Manter | Quote não traz "RhCE" nem a finalidade. |
| 14 | TG 442A | b) Método OECD TG 442A e 442B - Versões não radioativas do Ensaio do Linfonodo Local. | LLNA:DA — Ensaio do Linfonodo Local Não Radioativo (ATP) | LLNA: DA — Non-Radioactive Local Lymph Node Assay (ATP) | Manter | Quote é único para 442A e 442B. |
| 15 | TG 442B | b) Método OECD TG 442A e 442B - Versões não radioativas do Ensaio do Linfonodo Local. | Sensibilização Cutânea: Ensaio de Linfonodo Local: BrdU-ELISA ou -FCM | Skin Sensitization: Local Lymph Node Assay: BrdU-ELISA or -FCM | Manter | Quote é único para 442A e 442B. |
| 22 | GD 129 | d) Método OECD TG 129 - estimativa da dose inicial para teste de toxicidade aguda oral sistêmica. | Citotoxicidade Basal para Estimativa de Dose Inicial de Toxicidade Aguda | Basal Cytotoxicity for Acute Toxicity Starting Dose Estimation | Manter | Quote diz "TG 129 – estimativa da dose inicial…"; nome é mais informativo (GD, não TG). |
| 30 | - | I - Técnica de Imunofluorescência Direta (Direct Fluorescent Antibody Test) - DFA Test; | Teste de Imunofluorescência Direta (DFA) para Diagnóstico de Raiva | Direct Fluorescent Antibody (DFA) Test for Rabies Diagnosis | Manter | Resolução diz "Técnica de…"; nome traz o contexto "raiva", que fica no cabeçalho do quote. |
| 33 | - | II - Teste Rápido de Imuno-histoquímica Direta (Direct Rapid Immunohistochemistry Test) - dRIT; | Teste rápido de imuno-histoquímica direta (dRIT) para diagnóstico da raiva | Direct rapid immunohistochemistry test (dRIT) for rabies diagnosis | Manter | Idem 30. |
| 34 | - | IV - Isolamento viral em cultivo celular (Rabies Tissue Culture Infection Test - RTCIT). | Teste de Infecção em Cultura de Tecidos para Raiva (RTCIT) | Rabies Tissue Culture Infection Test (RTCIT) | Manter | Resolução diz "Isolamento viral em cultivo celular", termo diferente. |
| 35 | - | III - Técnicas moleculares baseadas em Reação de Transcriptase Reversa, seguida de Reação em Cadeia da Polimerase quantitativa (RT-qPCR) ou convencional (RT-PCR); e | Ensaios de RT-PCR para Diagnóstico de Raiva | Rabies RT-PCR Diagnostic Assay | Manter | Quote é mais amplo (RT-qPCR ou RT-PCR). |
| 37 | TG 422 | b) Método OECD TG 422 - Estudo de toxicidade repetida combinado com teste de toxicidade reprodutiva; e | Estudo de Toxicidade por Doses Repetidas Combinado com o Teste de Triagem de Toxicidade Reprodutiva/Desenvolvimental | Combined Repeated Dose Toxicity Study with the Reproduction/Developmental Toxicity Screening Test | Manter | Resolução omite "triagem" e "desenvolvimento". |
| 39 | TG 492B | o Conselho Nacional de Controle de Experimentação Animal reconhece o método alternativo descrito no guia de testes da OECD TG 492B - Epitélio semelhante à córnea humana reconstruído (Reconstructed Human Cornea-like Epithelium (RhCE) Test Method for Eye Hazard Identification) para avaliação do desfecho: danos oculares severos e irritação ocular. | Método de Teste de Epitélio Corneano Humano Reconstruído (RhCE) para Identificação de Perigo Ocular | Reconstructed Human Cornea-like Epithelium (RhCE) Test Method for Eye Hazard Identification | Manter | Quote é uma frase longa; nome já traduz o título da TG. |
| 40 | TG 491 | a) Método OECD TG 491 - Teste in vitro de curta duração para danos oculares; | Método de Teste In Vitro de Exposição de Curta Duração para Identificação de Substâncias Químicas que Induzem Lesões Oculares Graves e Substâncias que Não Requerem Classificação para Irritação Ocular ou Lesão Ocular Grave | Short Time Exposure In Vitro Test Method for Identifying Chemicals Inducing Serious Eye Damage and Chemicals Not Requiring Classification for Eye Irritation or Serious Eye Damage | Manter | Quote é mais curto; perde "exposição" e "identificação". |
| 41 | TG 455 | a) Método OECD TG 455 - Teste baseado na performance para ensaios in vitro de transativação transfectada estável para detectar agonistas e antagonistas de receptor estrogênico. | Diretriz de Teste Baseada em Desempenho para Ensaios de Transativação In Vitro estavelmente Transfectados para Detectar Agonistas e Antagonistas do Receptor de Estrogênio | Performance-Based Test Guideline for Stably Transfected Transactivation In Vitro Assays to Detect Estrogen Receptor Agonists and Antagonists | Manter | Diferença só de estilo ("transfectada estável"). |
| 42 | TG 493 | b) Método OECD TG 493 - Teste baseado na performance para ensaios in vitro de receptor estrogênico humano recombinante (hrER) para detectar substâncias químicas com afinidade de ligação ER. | Diretriz de Teste Baseada em Desempenho para Ensaios In Vitro com Receptor de Estrogênio Humano Recombinante (hrER) para Detectar Substâncias com Afinidade de Ligação ao RE | Performance-Based Test Guideline for Human Recombinant Estrogen Receptor (hrER) In Vitro Assays to Detect Chemicals with ER Binding Affinity | Manter | Diferença só de estilo ("ER" em vez de "RE"). |
| 44 | TG 458 | a) Método OECD TG 458 - Ensaio de ativação transcripcional de receptores androgênicos humanos transfectados para detecção de atividade agonista e antagonista de substâncias químicas. | Ensaio de Ativação Transcricional do Receptor de Andrógeno Humano estavelmente transfectado | Stably Transfected Human Androgen Receptor Transcriptional Activation Assay | Manter | Resolução diz "transfectados" e perde "estavelmente". |
| 47 | TG 494 | a) Método OECD TG 494 - Vitrigel - Teste de irritação ocular para identificação de substâncias químicas que não requerem classificação e rotulagem para irritação ocular ou sério dano ocular. | Método de Teste de Irritação Ocular Vitrigel | Vitrigel - Eye Irritancy Test Method | Manter | Quote é o título completo, mais longo que o nome. |
| 49 | TG 496 | b) Método OECD TG 496 - Teste macromolecular in vitro para identificação de substâncias químicas que induzem dano ocular severo e substâncias químicas que não requerem classificação para irritação ocular ou dano ocular severo. | Método de teste macromolecular in vitro para identificar produtos químicos que induzem lesões oculares graves e produtos químicos que não requerem classificação para irritação ocular ou lesões oculares graves | In vitro Macromolecular Test Method for Identifying Chemicals Inducing Serious Eye Damage and Chemicals Not Requiring Classification for Eye Irritation or Serious Eye Damage | Manter | Quote usa "dano ocular severo"; nome usa "lesões oculares graves" (título da TG). |
| 51 | TG 212 | a) Método OECD TG 212 - Peixe, teste de toxicidade a curto prazo em estágios embrionários e recém nascidos. | Teste de toxicidade de curto prazo em estágios de embrião e alevino de peixe | Fish, Short-term Toxicity Test on Embryo and Sac-Fry Stages | Manter | Quote diz "recém nascidos"; "alevino" (sac-fry) é mais preciso. |
| 56 | - | o Conselho Nacional de Controle de Experimentação Animal reconhece como método alternativo o Fator C recombinante (rFC) para detecção de endotoxinas bacterianas, descrito em Compêndios como a Farmacopeia Europeia (Test for bacterial endotoxins using recombinant factor C). | Teste de endotoxinas bacterianas com fator C recombinante (rFC) | Bacterial Endotoxins Test Using Recombinant Factor C (rFC) | Manter | Quote sem título próprio; nome é mais descritivo. |

### A.3 Nomes em inglês diferentes do título do documento-fonte (4 restantes)

O plano manda manter, em inglês, o nome como está no documento oficial. Comparei o `name->>'en-us'` com o título do documento cadastrado em `source_doc_id`. Os 15 métodos abaixo divergem. Quando o documento cadastrado é um manual ou uma coleção (Farmacopeia Brasileira, WOAH), não há título por método para comparar, e a coluna de título oficial indica o que conferir. Os títulos oficiais das TGs vêm do cabeçalho dos PDFs em `docs/oecd_files`. Onze nomes já foram alinhados ao título oficial: TG 430, 437, 429, 491, rFC (migration 091), os quatro de raiva, pelo capítulo 3.1.19 da WOAH (migration 095), e MAT e LAL, pelos títulos da Farmacopeia Europeia (migration 103), por não conflitarem com o nome em português da RN. O capítulo da Farmacopeia Brasileira do LAL não traz título em inglês. Os que restam têm conflito com o texto da RN, dependem da confirmação do item 12 ou não têm documento-fonte no repositório.

| ID | Ref. | Nome atual (en-us) | Título oficial | Diferença |
|---|---|---|---|---|
| 11 | TG 442D | In Vitro Skin Sensitisation: Key Event on Keratinocyte Activation | In Vitro Skin Sensitisation (subtítulo: Assays addressing the Adverse Outcome Pathway Key Event on Keratinocyte activation) | Subtítulo é paráfrase (item 12) |
| 12 | TG 442E | In Vitro Skin Sensitisation: Key Event on Dendritic Cell Activation | In Vitro Skin Sensitisation (subtítulo: In Vitro Skin Sensitisation assays addressing the Key Event on activation of dendritic cells on the Adverse Outcome Pathway for Skin Sensitisation) | Subtítulo é paráfrase (item 12) |
| 14 | TG 442A | LLNA: DA — Non-Radioactive Local Lymph Node Assay (ATP) | Skin Sensitization: Local Lymph Node Assay: DA | Redação própria |
| 22 | GD 129 | Basal Cytotoxicity for Acute Toxicity Starting Dose Estimation | Guidance Document on Using Cytotoxicity Tests to Estimate Starting Doses for Acute Oral Systemic Toxicity Tests | Redação própria. O cadastro do documento 11 escreve "Systematic" em vez de "Systemic": conferir |

## Apêndice B. Situação do sistema frente ao plano de revisão (`Revisao.md`)

Resumo da revisão feita depois das migrations 068 a 090. "Conforme" quer dizer que o banco já segue o plano.

| Ponto do plano | Situação | Pendência |
|---|---|---|
| Nomes em inglês (oficiais) | 4 métodos ainda divergem do título do documento-fonte (11 foram corrigidos nas migrations 091, 095 e 103) | Item 12 e Apêndice A.3 |
| Nomes em português (como na RN) | 25 conformes; 22 diferem | Item 12 e Apêndice A.2 |
| Sistema de teste (6 categorias) | Conforme, com `in_data` aberto e sem `hybrid`; o banco ainda aceita `unclear` | Itens 9 e 12 |
| Status (5 categorias) | `recognized` existe, mas os 47 métodos continuam `validated`; faltam as duas categorias de literatura; sobram `partially_validated`, `not_validated` e `unclear` | Item 8 |
| Uso de animais (6 categorias) | Conforme nos valores e nos rótulos; 20 métodos continuam sem classificação (`NULL`) | Itens 1 a 6 |
| Referência: RNs | Conforme nos dados (regulação do Brasil com o documento); exibição na interface não verificada | Item 11 |
| Data limite de substituição (5 anos) | Conforme: datas e prazo em `regulations` (RN 18, 31 e 45 já vencidas) | Item 13 |
| 3Rs: substituição total ou parcial | Conforme: indicada em todos os `replacement_rationale` e em `animal_procedures_avoided`; glossário atualizado | Item 7 (confirmar a lista) |
| 3Rs: critérios de redução e refinamento | Revisão pelos critérios do plano ainda não feita; 9 métodos sem nenhum R | Item 7 |
| Finalidade e contexto de aplicação (8 valores) | Banco tem 10 (forense e outro a mais); nenhum método tem pesquisa básica ou aplicada | Item 14 |
| Endpoint específico | Conforme: MAT e TG 487 receberam os endpoints mais específicos; os gerais foram mantidos | Item 15 |
| Material ou sistema biológico | Conforme: 58 linhas para os 47 métodos, com a fonte de cada uma | Item 13 (confirmar espécies e S9) |
| Espécie | Conforme: tabela `species` com 13 espécies | Item 13 |
| Procedimento animal evitado | 36 de 47 métodos preenchidos; 3 têm R e não têm procedimento; 8 não têm R | Item 13 |
| Marca de revisado | `review_status` existe e os 47 métodos estão `in_review`; faltam revisor, data e as 10 perguntas de controle | Item 13 |
| Terminologia regulatória (aprovado, reconhecido, recomendado...) | `recognized` existe em `regulatory_status`, e as regulações do Brasil são `recognized`, as TGs da OECD `adopted` e o GD 129 `published` (migration 128) | Item 16 (decidido) |
| Redação final (clareza, sem exagero, limitações) | Revisão editorial das descrições e dos rationales ainda não feita | Fora do banco |
