# Karynn Review Checklist — 3R Assist Methods Database

> **Propósito:** Confirmar todos os campos `[VERIFY]` e preencher contextos de validação antes de `active = TRUE`.
> Nenhum método é retornado ao usuário até que `active = TRUE` seja definido.
>
> **Comando para ativar após revisão completa:**
> ```sql
> UPDATE methods SET active = TRUE, updated_at = NOW() WHERE slug = '<slug>';
> ```
>
> **Como usar:**
> 1. Completar a seção **Campos globais** antes de revisar métodos individuais.
> 2. Para cada método: confirmar campos do método + preencher tabela de contextos de validação.
> 3. Marcar ☑ e registrar valor confirmado ou "sem alteração".
> 4. Executar UPDATE SQL.
> 5. Registrar data e observações na tabela-resumo.

---

## Tabela-resumo

| # | Slug | Endpoint | Contextos seeded | active | Data | Obs |
|---|---|---|---|---|---|---|
| 1 | oecd-tg439-epiderm | skin_irritation | brazil·oecd | ☐ | | |
| 2 | oecd-tg439-episkin | skin_irritation | brazil·oecd | ☐ | | |
| 3 | oecd-tg431-rhe-corrosion | skin_corrosion | brazil·oecd | ☐ | | |
| 4 | oecd-tg430-ter-corrosion | skin_corrosion | brazil·oecd | ☐ | | |
| 5 | oecd-tg435-membrane-barrier | skin_corrosion | brazil·oecd | ☐ | | |
| 6 | oecd-tg437-bcop | ocular_irritation | brazil·oecd | ☐ | | |
| 7 | oecd-tg438-ice | ocular_irritation | brazil·oecd | ☐ | | |
| 8 | oecd-tg492-rce | ocular_irritation | oecd only | ☐ | | |
| 9 | oecd-tg460-fluorescein-leakage | ocular_irritation | brazil·oecd | ☐ | | |
| 10 | oecd-tg442c-dpra | skin_sensitisation | oecd only | ☐ | | |
| 11 | oecd-tg442d-keratinosens | skin_sensitisation | oecd only | ☐ | | |
| 12 | oecd-tg442e-hclat | skin_sensitisation | oecd only | ☐ | | |
| 13 | oecd-tg429-llna | skin_sensitisation | brazil·oecd | ☐ | | |
| 14 | oecd-tg442a-llna-da | skin_sensitisation | brazil·oecd | ☐ | | |
| 15 | oecd-tg442b-llna-brdu | skin_sensitisation | brazil·oecd | ☐ | | |
| 16 | oecd-tg432-3t3nru | phototoxicity | brazil·oecd | ☐ | | |
| 17 | oecd-tg428-skin-absorption-vitro | skin_absorption | brazil·oecd | ☐ | | |
| 18 | oecd-tg471-ames | genotoxicity | brazil·oecd | ☐ | | |
| 19 | oecd-tg476-hprt | genotoxicity | brazil·oecd | ☐ | | |
| 20 | oecd-tg487-micronucleus | genotoxicity | brazil·oecd | ☐ | | |
| 21 | mat-monocyte-activation | pyrogenicity | brazil⚠️·(no oecd TG) | ☐ | | |
| 22 | niceatm-cytotox-basal-barranco | acute_toxicity | brazil·oecd·us | ☐ | | |
| 23 | oecd-tg420-fixed-dose | acute_toxicity | brazil·oecd | ☐ | | |
| 24 | oecd-tg423-atc | acute_toxicity | brazil·oecd | ☐ | | |
| 25 | oecd-tg425-udp | acute_toxicity | brazil·oecd | ☐ | | |

---

## Campos globais (fazer antes de revisar métodos individuais)

### 1. NCIt — mapear endpoint_category → ID

Acessar https://ncit.nci.nih.gov/ e buscar cada endpoint. Após confirmar:
```sql
UPDATE methods SET ncit_id = '<ID>' WHERE endpoint_category = '<endpoint>';
```

| endpoint_category | NCIt ID | NCIt preferred label | ☐/☑ |
|---|---|---|---|
| acute_toxicity | [VERIFY] | | ☐ |
| skin_irritation | [VERIFY] | | ☐ |
| skin_corrosion | [VERIFY] | | ☐ |
| ocular_irritation | [VERIFY] | | ☐ |
| skin_sensitisation | [VERIFY] | | ☐ |
| phototoxicity | [VERIFY] | | ☐ |
| genotoxicity | [VERIFY] | | ☐ |
| pyrogenicity | [VERIFY] | | ☐ |
| skin_absorption | [VERIFY] | | ☐ |

### 2. source_db — confirmar por método

Os textos de `description_en` e `description_pt` foram escritos a partir de documentos OECD TG diretamente (`OECD_TG`) ou adaptados de entradas ECVAM DB-ALM (`ECVAM_DBALM`)? Se diferente por método, listar exceções aqui e executar UPDATE individual.

- ☐ Confirmado: todos os 23 métodos OECD usam `source_db = 'OECD_TG'`
- ☐ Exceções (listar slugs + source_db correto):

### 3. application_ids — confirmar fallback `basic-research`

Métodos mapeados de `study_domain = 'general'` receberam `application_ids` → `basic-research`. Confirmar se algum deveria ser `regulatory-use` (ou outro slug em `applications`) dado uso regulatório típico.

- ☐ Confirmado sem alterações
- ☐ Exceções (listar slugs + application correto):

### 4. Contextos EU — [VERIFY para todos os métodos]

Os contextos `eu` não foram seeded por falta de referência específica confirmada. Após verificar contra EU Cosmetics Regulation 1223/2009 (para métodos relevantes para cosméticos) e REACH Annex (para químicos industriais), inserir:

```sql
INSERT INTO method_regulatory_contexts
    (method_id, jurisdiction, validation_status, regulatory_body, regulation_date, regulatory_citation)
VALUES
    ((SELECT id FROM methods WHERE slug='<slug>'),
     'general', 'eu', 'validated', 'ECHA', 'YYYY-MM-DD', '<URL>');
```

Métodos com maior probabilidade de contexto EU validado:
- TG 432 (3T3 NRU): EU Cosmetics Reg 1223/2009 Annex — fototoxicidade obrigatória para cosméticos
- TG 439 (EpiDerm, EpiSkin): EU Cosmetics Reg — irritação cutânea obrigatória
- TG 437/438/460: EU Cosmetics Reg — irritação ocular
- TG 429/442C/D/E: EU Cosmetics Reg + REACH — sensibilização

### 5. Rationales 3R — preencher nos 25 seeded (ADR-023)

Cada R aplicável tem uma coluna JSONB localizada: `replacement_rationale`, `reduction_rationale`, `refinement_rationale` (`{"en-us","pt-br"}`).
Valor não-nulo/não-vazio = o método qualifica para aquele R; o texto é a justificativa auditável.

Após a migração `007` + `backfill_3r_rationales.py`, colunas aplicáveis contêm o placeholder
`[PENDENTE — ver category_3r]`. Substituir pelo texto real (PT ou EN, preferência CEUA).

Colunas `NULL` = aquele R **não se aplica** (não preencher com string vazia).

Para preencher:
```sql
UPDATE methods
SET replacement_rationale = '{"en-us":"<justificativa>", "pt-br":"<justificativa>"}'::jsonb
WHERE slug = '<slug>';
-- idem reduction_rationale / refinement_rationale
```

Listar pendências (gate antes do DROP de `category_3r`):
```bash
python scripts/backfill_3r_rationales.py --check
```

**Casos ambíguos (decidir quais colunas preencher e com qual texto):**

| Slug | Placeholder inicial | Questão |
|---|---|---|
| oecd-tg429-llna | `replacement_rationale` | Substitui cobaia (replacement) mas ainda usa camundongo. CEUAs brasileiras classificam como replacement ou também reduction/refinement? |
| oecd-tg442a-llna-da | `refinement_rationale` | Refinamento do TG 429 (sem radioatividade). Também é replacement em relação ao GPMT? Se sim, preencher `replacement_rationale` e deixar `refinement_rationale` (ou ambos). |
| oecd-tg442b-llna-brdu | `refinement_rationale` | Mesma questão do TG 442A |
| oecd-tg420 / 423 / 425 | `reduction_rationale` + `refinement_rationale` | Confirmar se CEUAs reconhecem a dupla classificação |

### 6. Keywords — complementar com terminologia CEUA

As colunas `keywords` em `methods` (`{"en-us": [...], "pt-br": [...]}`) são um conjunto representativo. Adicionar termos que você usa em comunicações com CEUAs e pesquisadores brasileiros.

---

## Revisão por método

> Para cada método: confirmar campos do método + preencher `*_rationale` (ADR-023) + contextos de validação faltantes.
> Placeholders `[PENDENTE — ver category_3r]` devem ser substituídos por justificativa real antes do DROP de `category_3r`.
> Os contextos `brazil` e `oecd` já estão seeded onde confirmados; indicar se precisam de correção.
> Adicionar `eu`, `us`, e qualquer contexto por jurisdição específica que se aplicar.

---

### Template de contexto para INSERT

```sql
INSERT INTO method_regulatory_contexts
    (method_id, jurisdiction, validation_status,
     regulatory_body, regulation_date, regulatory_citation, notes)
VALUES
    ((SELECT id FROM methods WHERE slug='<slug>'),
     '<jurisdiction>', '<validation_status>',
     '<regulatory_body>', 'YYYY-MM-DD', '<citation>', '<notes>');
```

---

### 1–2. oecd-tg439-epiderm / oecd-tg439-episkin

**Campos:**
- ☐ `name_pt` adequado para CEUA?
- ☐ `description_pt` clara para pesquisador sem familiaridade?
- ☐ `source_db` confirmado (ver campo global)
- ☐ `text_for_embedding` adequado?
- ☐ **`replacement_rationale`**: substituir placeholder por justificativa auditável

**Contextos seeded:** brazil (CONCEA, RN 18/2014) · oecd (TG 439)

**Contextos a verificar:**

| jurisdiction | validation_status | regulatory_body | regulation_date | ☐/☑ |
|---|---|---|---|---|---|
| cosmetics | eu | validated | ECHA/JRC | EU Cosmetics Reg 1223/2009 | ☐ |
| general | eu | validated | ECHA | REACH Reg 1907/2006 | ☐ |
| general | us | accepted | ICCVAM | [VERIFY] | ☐ |

**Notas:**

---

### 3. oecd-tg431-rhe-corrosion

**Campos:**
- ☐ `name_pt` · ☐ `description_pt` · ☐ `source_db` · ☐ `text_for_embedding`
- ☐ **`replacement_rationale`**: substituir placeholder por justificativa auditável

**Contextos seeded:** brazil · oecd (TG 431)

| jurisdiction | validation_status | regulatory_body | regulation_date | ☐/☑ |
|---|---|---|---|---|---|
| general | eu | validated | ECHA | REACH Annex VIII | ☐ |
| general | us | accepted | ICCVAM | [VERIFY] | ☐ |

**Notas:**

---

### 4. oecd-tg430-ter-corrosion

**Campos:** ☐ `name_pt` · ☐ `description_pt` · ☐ `source_db` · ☐ `text_for_embedding`
- ☐ **`replacement_rationale`**: substituir placeholder por justificativa auditável

**Contextos seeded:** brazil · oecd (TG 430)

| jurisdiction | validation_status | regulatory_body | regulation_date | ☐/☑ |
|---|---|---|---|---|---|
| general | eu | validated | ECHA | REACH Annex VIII | ☐ |

**Notas:**

---

### 5. oecd-tg435-membrane-barrier

**Campos:** ☐ `name_pt` · ☐ `description_pt` · ☐ `source_db` · ☐ `text_for_embedding`
- ☐ **`replacement_rationale`**: substituir placeholder por justificativa auditável
- ☐ Nota de aplicabilidade (pH < 2 ou > 11,5) está clara para o usuário no S3?

**Contextos seeded:** brazil · oecd (TG 435)

| jurisdiction | validation_status | regulatory_body | regulation_date | ☐/☑ |
|---|---|---|---|---|---|
| chemical_safety | eu | validated | ECHA | REACH Annex VIII | ☐ |

**Notas:**

---

### 6. oecd-tg437-bcop

**Campos:** ☐ `name_pt` · ☐ `description_pt` · ☐ `source_db` · ☐ `text_for_embedding`
- ☐ **`replacement_rationale`**: substituir placeholder por justificativa auditável

**Contextos seeded:** brazil · oecd (TG 437)

| jurisdiction | validation_status | regulatory_body | regulation_date | ☐/☑ |
|---|---|---|---|---|---|
| cosmetics | eu | validated | ECHA/JRC | EU Cosmetics Reg 1223/2009 | ☐ |
| general | eu | validated | ECHA | REACH Annex VIII | ☐ |
| general | us | accepted | ICCVAM | [VERIFY] | ☐ |

**Notas:**

---

### 7. oecd-tg438-ice

**Campos:** ☐ `name_pt` · ☐ `description_pt` · ☐ `source_db` · ☐ `text_for_embedding`
- ☐ **`replacement_rationale`**: substituir placeholder por justificativa auditável

**Contextos seeded:** brazil · oecd (TG 438)

| jurisdiction | validation_status | regulatory_body | regulation_date | ☐/☑ |
|---|---|---|---|---|---|
| cosmetics | eu | validated | ECHA/JRC | EU Cosmetics Reg 1223/2009 | ☐ |
| general | eu | validated | ECHA | REACH Annex VIII | ☐ |

**Notas:**

---

### 8. oecd-tg492-rce ⚠️ sem contexto brazil

**Campos:** ☐ `name_pt` · ☐ `description_pt` · ☐ `source_db` · ☐ `text_for_embedding`
- ☐ **`replacement_rationale`**: substituir placeholder por justificativa auditável

**Contextos seeded:** oecd only (TG 492, publicado 2019, pós-RN 18/2014)

- ☐ **Verificar se CONCEA emitiu RN posterior adotando TG 492.** Se sim, inserir contexto brazil.

| jurisdiction | validation_status | regulatory_body | regulation_date | ☐/☑ |
|---|---|---|---|---|---|
| general | brazil | validated | CONCEA | [RN posterior — VERIFY] | ☐ |
| cosmetics | eu | validated | ECHA/JRC | EU Cosmetics Reg 1223/2009 | ☐ |

**Notas:**

---

### 9. oecd-tg460-fluorescein-leakage

**Campos:** ☐ `name_pt` · ☐ `description_pt` · ☐ `source_db` · ☐ `text_for_embedding`
- ☐ **`replacement_rationale`**: substituir placeholder por justificativa auditável

**Contextos seeded:** brazil · oecd (TG 460)

| jurisdiction | validation_status | regulatory_body | regulation_date | ☐/☑ |
|---|---|---|---|---|---|
| cosmetics | eu | validated | ECHA/JRC | EU Cosmetics Reg 1223/2009 | ☐ |

**Notas:**

---

### 10–12. oecd-tg442c-dpra / oecd-tg442d-keratinosens / oecd-tg442e-hclat ⚠️ sem brazil

**Campos (cada um):** ☐ `name_pt` · ☐ `description_pt` · ☐ `source_db` · ☐ `text_for_embedding`
- ☐ **`replacement_rationale`**: substituir placeholder por justificativa auditável

**Contextos seeded:** oecd only (TG 442C/D/E publicados 2015–2017, pós-RN 18)

- ☐ **Verificar se CONCEA emitiu RN adotando TG 442C/D/E.** Se sim, inserir contextos brazil.

| jurisdiction | validation_status | regulatory_body | regulation_date | ☐/☑ |
|---|---|---|---|---|---|
| general | brazil | validated | CONCEA | [RN posterior — VERIFY] | ☐ |
| cosmetics | eu | validated | ECHA/JRC | EU Cosmetics Reg 1223/2009 | ☐ |
| chemical_safety | eu | validated | ECHA | REACH Annex VIII | ☐ |

**Notas:**

---

### 13. oecd-tg429-llna ⚠️ rationales 3R a confirmar

**Campos:** ☐ `name_pt` · ☐ `description_pt` · ☐ `source_db` · ☐ `text_for_embedding`
- ☐ **`replacement_rationale`**: placeholder inicial (substitui GPMT/Buehler em cobaia). Confirmar se CEUAs tratam LLNA como replacement; se sim, preencher justificativa.
- ☐ **`reduction_rationale` / `refinement_rationale`**: preencher **somente se** CEUAs também classificarem LLNA nesses Rs (ainda usa camundongo); caso contrário deixar `NULL`.

**Contextos seeded:** brazil · oecd (TG 429)

| jurisdiction | validation_status | regulatory_body | regulation_date | ☐/☑ |
|---|---|---|---|---|---|
| cosmetics | eu | validated | ECHA/JRC | EU Cosmetics Reg 1223/2009 | ☐ |
| chemical_safety | eu | validated | ECHA | REACH Annex VIII | ☐ |

**Notas:**

---

### 14–15. oecd-tg442a-llna-da / oecd-tg442b-llna-brdu ⚠️ rationales 3R a confirmar

**Campos (cada):** ☐ `name_pt` · ☐ `description_pt` · ☐ `source_db` · ☐ `text_for_embedding`
- ☐ **`refinement_rationale`**: placeholder inicial (elimina radioatividade vs TG 429). Preencher justificativa.
- ☐ **`replacement_rationale`**: preencher **somente se** também for replacement em relação ao GPMT; caso contrário deixar `NULL`.

**Contextos seeded:** brazil · oecd (TG 442A / TG 442B)

| jurisdiction | validation_status | regulatory_body | regulation_date | ☐/☑ |
|---|---|---|---|---|---|
| cosmetics | eu | validated | ECHA/JRC | EU Cosmetics Reg 1223/2009 | ☐ |

**Notas:**

---

### 16. oecd-tg432-3t3nru

**Campos:** ☐ `name_pt` · ☐ `description_pt` · ☐ `source_db` · ☐ `text_for_embedding`
- ☐ **`replacement_rationale`**: substituir placeholder por justificativa auditável

**Contextos seeded:** brazil · oecd (TG 432)

| jurisdiction | validation_status | regulatory_body | regulation_date | ☐/☑ |
|---|---|---|---|---|---|
| cosmetics | eu | validated | ECHA/JRC | EU Cosmetics Reg 1223/2009 Annex | ☐ |
| pharma | eu | accepted | EMA | [VERIFY guideline ref] | ☐ |

**Notas:**

---

### 17. oecd-tg428-skin-absorption-vitro

**Campos:** ☐ `name_pt` · ☐ `description_pt` · ☐ `source_db` · ☐ `text_for_embedding`
- ☐ **`replacement_rationale`**: substituir placeholder por justificativa auditável

**Contextos seeded:** brazil · oecd (TG 428)

| jurisdiction | validation_status | regulatory_body | regulation_date | ☐/☑ |
|---|---|---|---|---|---|
| chemical_safety | eu | validated | ECHA | REACH Annex VIII | ☐ |
| pharma | eu | accepted | EMA | [VERIFY] | ☐ |

**Notas:**

---

### 18–20. oecd-tg471-ames / oecd-tg476-hprt / oecd-tg487-micronucleus

**Campos (cada):** ☐ `name_pt` · ☐ `description_pt` · ☐ `source_db` · ☐ `text_for_embedding`
- ☐ **`replacement_rationale`**: substituir placeholder por justificativa auditável

**Contextos seeded:** brazil · oecd (TG 471 / TG 476 / TG 487)

| jurisdiction | validation_status | regulatory_body | regulation_date | ☐/☑ |
|---|---|---|---|---|---|
| pharma | eu | validated | EMA | ICH S2(R1) | ☐ |
| pharma | us | validated | FDA | ICH S2(R1) | ☐ |
| chemical_safety | eu | validated | ECHA | REACH Annex VII | ☐ |
| chemical_safety | us | validated | EPA | OCSPP 870.5100 / 870.5300 | ☐ |

**Notas:**

---

### 21. mat-monocyte-activation ⚠️ múltiplos [VERIFY]

**Campos:**
- ☐ `name_pt`
- ☐ `description_pt`
- ☐ `source_db` — confirmar: `FARMACOPEIA_BR` ou outra fonte primária?
- ☐ `oecd_ref` — atualmente NULL. MAT não tem TG OECD standalone; verificar se GD 129 ou EP 2.6.30 é a referência adequada
- ☐ `text_for_embedding`
- ☐ **`replacement_rationale`**: substituir placeholder por justificativa auditável

**Contextos seeded:** brazil ⚠️ (ANVISA como regulatory_body — [VERIFY])

- ☐ **Confirmar**: Farmacopeia Brasileira capítulo exato que descreve MAT + regulatory_body correto (ANVISA ou CONCEA)
- ☐ Após confirmação, atualizar o contexto brazil:
  ```sql
  UPDATE method_regulatory_contexts
  SET regulatory_body = '<body>', regulation_date = 'YYYY-MM-DD', notes = NULL
  WHERE method_id = (SELECT id FROM methods WHERE slug = 'mat-monocyte-activation')
    AND jurisdiction = 'brazil';
  ```

| jurisdiction | validation_status | regulatory_body | regulation_date | ☐/☑ |
|---|---|---|---|---|---|
| pharma | eu | validated | EDQM | [VERIFY date] | ☐ |
| pharma | us | accepted | FDA | [VERIFY date] | ☐ |

**Notas:**

---

### 22. niceatm-cytotox-basal-barranco ⚠️ jurisdição brazil a confirmar

**Campos:**
- ☐ `name_pt`
- ☐ `description_pt`
- ☐ `source_db` — `NICEATM`; confirmar referência primária (Barranco et al. — qual publicação?)
- ☐ `text_for_embedding`
- ☐ **`replacement_rationale`**: substituir placeholder (substitui dose-ranging in vivo)
- ☐ **`reduction_rationale`**: substituir placeholder (reduz animais no estudo principal)

**Contextos seeded:** brazil (CONCEA, via GD 129 em RN 18 VI-d) · oecd (GD 129) · us (ICCVAM)

- ☐ **Confirmar** referência cruzada: GD 129 → RN 18 Art. 2 VI-d. Se confirmada, atualizar `regulation_date` / `notes` do contexto brazil:
  ```sql
  UPDATE method_regulatory_contexts
  SET regulation_date = 'YYYY-MM-DD',
      notes = 'RN 18/2014 Art. 2 VI-d (via OECD GD 129)'
  WHERE method_id = (SELECT id FROM methods WHERE slug = 'niceatm-cytotox-basal-barranco')
    AND jurisdiction = 'brazil';
  ```
- ☐ Confirmar publicação Barranco et al. e registrar citação em `regulatory_citation` do contexto `us` (ICCVAM/NICEATM), se aplicável.

**Notas:**

---

### 23–25. oecd-tg420 / oecd-tg423 / oecd-tg425 ⚠️ rationales 3R a confirmar

**Campos (cada):** ☐ `name_pt` · ☐ `description_pt` · ☐ `source_db` · ☐ `text_for_embedding`
- ☐ **`reduction_rationale`**: substituir placeholder (menos animais que LD50 clássica). Confirmar se CEUAs reconhecem reduction.
- ☐ **`refinement_rationale`**: substituir placeholder (endpoint de toxicidade evidente / procedimento humanizado). Confirmar se CEUAs reconhecem refinement; se preferirem um único R, preencher só esse e deixar o outro `NULL`.

**Contextos seeded:** brazil · oecd (TG 420 / TG 423 / TG 425)

| jurisdiction | validation_status | regulatory_body | regulation_date | ☐/☑ |
|---|---|---|---|---|---|
| chemical_safety | eu | validated | ECHA | REACH Annex B.1 tris | ☐ |
| pharma | eu | accepted | EMA | [VERIFY] | ☐ |
| general | us | validated | EPA | OCSPP 870.1100 | ☐ |

**Notas:**

---

## Questões para discussão com Leo

1. **Tempo por entrada**: registrar quanto tempo levou para revisar um método completo (campos + contextos). Este dado é necessário para fechar H5 (tractability).

2. **Contextos por jurisdição**: para os métodos que têm usos regulatórios distintos entre frameworks (ex: genotoxicidade sob ICH S2 vs. REACH), vale criar contextos separados por jurisdição agora ou no Phase 3?

3. **MAT sem TG OECD**: se a Farmacopeia Brasileira não tiver capítulo MAT específico, reconsiderar `source_db` e criar contexto a partir da Ph. Eur. 2.6.30 com `jurisdiction = 'eu'` como contexto primário.

---

*Criado em M3. Atualizado com study_domain (ADR-020), method_regulatory_contexts (ADR-022), colunas `*_rationale` por R (ADR-023; supersede ADR-021).*
