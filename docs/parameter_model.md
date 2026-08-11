# Parameter Model — 3R Assist
> Version: MVP (Phase 1–2)
> Owner: Leo (implementation) · Karynn (vocabulary validation)
> Reference: spec.md §2.3 S2, §2.11 POST /analyze; decisions.md ADR-007

---

## 1. Propósito

Este documento define o contrato entre três componentes:
1. **ExtractionService** — o que o LLM extrai de um protocolo livre
2. **S2 (Parameter Review Screen)** — o que o usuário vê e pode corrigir
3. **RetrievalService** — o que alimenta filtros e embeddings para matching

Qualquer alteração neste modelo é uma mudança de interface, não de implementação.
Registrar como ADR se afetar o contrato do `POST /analyze`.

---

## 2. Campos e função de cada um

| Campo | Tipo | Obrigatório | Camada | Função |
|---|---|---|---|---|
| `endpoint_category` | enum (ver §3.1) | sim | **matching** | Hard filter — só retorna métodos com o mesmo endpoint |
| `route` | enum (ver §3.2), nullable | não | **matching** | Soft filter — exclui métodos com via incompatível |
| `study_domain` | enum (ver §3.3) | sim | **matching** | Soft filter — prioriza métodos do mesmo domínio de aplicação |
| `procedure_text` | string livre | não | **matching** | Concatenado ao embedding do protocolo |
| `species` | enum (ver §3.4), nullable | não | **display** | Exibido no S2; contexto para o usuário |
| `n_animals` | integer, nullable | não | **display** | Exibido no S2; contexto para o usuário |
| `regulatory` | boolean, nullable | não | **display** | Exibido no S2; contexto para o usuário |

Regra geral: campos **matching** são normalizados para valores de vocabulário controlado.
Campos **display** são extraídos em linguagem natural e exibidos sem normalização forçada.

---

## 3. Vocabulários controlados

### 3.1 `endpoint_category`

Vocabulário compartilhado entre o modelo de extração e a tabela `methods`.
O LLM deve mapear a descrição do protocolo para um desses valores.
Se o protocolo não se encaixar em nenhum: `null` (o usuário corrige no S2).

| Valor | Engloba | Métodos no banco (TG) |
|---|---|---|
| `acute_toxicity` | toxicidade aguda oral/ip/iv, LD50, DL50, classe tóxica | 420, 423, 425, GD129 |
| `skin_irritation` | irritação cutânea, dermal irritation, Draize pele | 439 |
| `skin_corrosion` | corrosão cutânea, dermal corrosion | 430, 431, 435 |
| `ocular_irritation` | irritação ocular, Draize olho, eye irritation | 437, 438, 460 |
| `skin_sensitisation` | sensibilização cutânea, alergenicidade, LLNA | 429, 442A, 442B, 442C, 442D, 442E |
| `phototoxicity` | fototoxicidade, photoirritation, 3T3 NRU | 432 |
| `genotoxicity` | genotoxicidade, mutagenicidade, micronúcleo, Ames | 471, 476, 487 |
| `pyrogenicity` | pirogenicidade, pirogênio, MAT | MAT |
| `skin_absorption` | absorção cutânea, penetração dérmica | 428 |
| `reproductive_toxicity` | toxicidade reprodutiva e do desenvolvimento, fertilidade, teratogenicidade | — |
| `endocrine_activity` | atividade endócrina, estrogênica, androgênica, esteroidogênica | — |
| `photoreactivity` | fotorreatividade, ROS sob luz | — |
| `aquatic_toxicity` | toxicidade aquática, embrião de peixe, estágios iniciais | — |
| `toxicokinetics` | toxicocinética, ADME, depuração intrínseca | — |
| `bacterial_endotoxin` | endotoxinas bacterianas, LAL/BET | — |
| `rabies_diagnosis` | diagnóstico da raiva | — |

Sinônimos comuns para instrução ao LLM:
- "teste de Draize" sem especificação → `null` (ambíguo: olho ou pele?)
- "DL50", "dose letal", "LC50 oral" → `acute_toxicity`
- "sensibilização", "alergenicidade", "patch test" → `skin_sensitisation`
- "irritação ocular", "conjuntival" → `ocular_irritation`
- "genotox", "mutagênese", "clastogenicidade" → `genotoxicity`

### 3.2 `route`

Via de administração ou exposição do protocolo.
Usado para filtrar métodos incompatíveis.

**Regra crítica:** `route` descreve como a substância de teste entra em contato com
o sistema biológico — não o tipo de sistema biológico. Para preparações ex vivo
(córneas isoladas, discos de pele, membranas), usar a rota que descreve o contato
da substância com o tecido, não o tipo de cultura.

| Valor | Sinônimos | Métodos compatíveis (endpoint_category) |
|---|---|---|
| `oral` | p.o., gavagem, intragástrico, oral, gastric tube, gastric intubation, dietary (mixed in feed) | acute_toxicity |
| `intraperitoneal` | i.p. | acute_toxicity |
| `intravenous` | i.v., endovenoso | acute_toxicity |
| `dermal` | tópico, cutâneo, epitelial, epicutâneo, ex vivo skin disc application, membrane model | skin_irritation, skin_corrosion, skin_sensitisation, skin_absorption, phototoxicity |
| `ocular` | ocular, conjuntival, instilação ocular, applied over cornea, applied to corneal surface, ex vivo corneal application, topical to cornea | ocular_irritation |
| `inhalation` | inalação, respiratório, aerossol, nose-only chamber | (sem métodos no banco MVP) |
| `other` | qualquer via química não coberta pela lista controlada | (sem mapeamento em `route_endpoints` no MVP) |
| `null` | irradiação UV, exposição física, radiation — not a chemical route; também células em meio sem superfície tecidual orientada (usar `test_system: in_vitro`) | — |

> Vocabulários de `endpoint_category`, `route` e `study_domain` vivem nas tabelas PostgreSQL `endpoints`, `routes` e `study_domains` (`003_vocabulary_tables.sql`). Compatibilidade rota↔endpoint: tabela `route_endpoints`. Ver `docs/tables.md`.
> Modalidade de ensaio (in silico / in chemico / in vitro / ex vivo / in vivo) NÃO é `route` — usar `methods.test_system`.

**Disambiguação ex vivo vs. cultura celular:**

| Sistema | `route` correto | Raciocínio |
|---|---|---|
| Córnea bovina em câmara de perfusão (EVEIT) + substância aplicada sobre ápice | `ocular` | A substância toca a superfície corneana — contato ocular |
| Disco de pele excisada + substância aplicada topicamente | `dermal` | A substância toca a superfície dérmica — contato dérmico |
| Células em placa, substância adicionada ao meio | `null` (+ `test_system: in_vitro`) | Não há superfície tecidual orientada; modalidade vai em `test_system` |
| Membrana sintética (p.ex. Strat-M) + substância tópica | `dermal` | Superfície orientada, contato dérmico análogo |

Quando o protocolo usa múltiplas vias (ex: `p.o. / i.p.`):
→ Extrair como array: `["oral", "intraperitoneal"]`
→ O RetrievalService inclui métodos compatíveis com QUALQUER das vias listadas

Quando `route` é `null`:
→ Sem filtro de via; o RetrievalService retorna todos os métodos do endpoint

### 3.3 `study_domain`

Domínio de aplicação do protocolo. Responde à pergunta "em qual domínio este estudo existe?" — não implica que um framework regulatório necessariamente existe. Determina relevância de indicadores de jurisdição e priorização de métodos no RetrievalService.

> **ADR-020:** renomeado de `application_area` para `study_domain`. Ver `decisions.md`.

**Vocabulário MVP (Phase 1–2):**

| Valor | Quando usar |
|---|---|
| `pharma` | segurança farmacêutica, testes regulatórios de medicamentos, vacinas, dispositivos médicos |
| `cosmetics` | cosméticos, produtos de higiene pessoal |
| `chemical_safety` | substâncias químicas, agrotóxicos, produtos industriais, ingredientes alimentares (food additive safety) |
| `general` | fallback — múltiplos domínios, não determinável, ou validação de método alternativo |

**Vocabulário Phase 3 (candidatos — pendente validação por Karynn):**

| Valor | Quando usar |
|---|---|
| `behavioral` | neurociência comportamental, modelos de ansiedade, depressão, dor, cognição, vício |
| `education` | treinamento cirúrgico, demonstração de técnicas, ensino de procedimentos |
| `basic_research` | pesquisa sem aplicação regulatória ou domínio setorial declarado |

Esses valores não devem ser adicionados ao vocabulário ativo até que (a) Karynn confirme que protocolos do piloto os requerem e (b) existam métodos correspondentes no banco. Adicionar valores sem cobertura no banco gera expectativa falsa no S2.

**Regra de fallback:** se não for possível determinar com segurança → `general`.

**Regras adicionais para `general`:**
1. O estudo valida ou caracteriza um método alternativo (o objeto é o método em si, não um produto específico). Ex: EVEIT validação com BAC + lágrima artificial → `general`.
2. As substâncias testadas pertencem a múltiplos domínios sem um predominante.
3. Nenhum dos valores MVP se aplica com segurança.

**Regra para `chemical_safety` vs. `pharma`/`cosmetics`:** o campo descreve o contexto do estudo, não da substância isolada. BAC (benzalkonium chloride) é usado em cosméticos E em fármacos E como preservante industrial — a presença de BAC sozinha não determina `cosmetics`.

### 3.4 `species` (display-only)

Normalizar para identificação no S2. Não usado em filtros.

| Valor | Sinônimos |
|---|---|
| `rat` | rato, Rattus norvegicus, Wistar, Sprague-Dawley, Fischer |
| `mouse` | camundongo, Mus musculus, BALB/c, C57BL/6 |
| `rabbit` | coelho, Oryctolagus cuniculus |
| `guinea_pig` | cobaia, Cavia porcellus |
| `chicken` | galinha, frango, Gallus gallus |
| `zebrafish` | peixe-zebra, Danio rerio |
| `in_vitro` | células, cultura celular, linhagem celular |
| `other` | qualquer espécie não listada acima |

---

## 4. Schema do objeto de extração (`ExtractionResult`) e resposta (`AnalyzeResponse`)

> ADR-014: array `experiments[]` + campo `notes`.
> ADR-015: two-stage extraction — `RawExtraction` (LLM) + `endpoint_category` (application code).
> ADR-016: evidence field paired with every extracted value; `raw_text_excerpt` removed.
> ADR-017: `n_animals` replaced by `AnimalCounts`.
> ADR-018: per-field `{field}_confidence` on `RawExtraction`; no top-level confidence.
> Mudança de contrato — qualquer alteração adicional requer novo ADR.

```python
# app/domain/extraction.py

from dataclasses import dataclass
from typing import Optional

# ── Stage 1: LLM output ──────────────────────────────────────────────────────

@dataclass
class AnimalCounts:
    female:    Optional[int]   # explicitly stated female count
    male:      Optional[int]   # explicitly stated male count
    total:     Optional[int]   # explicitly stated total (not derived)
    per_group: Optional[int]   # explicitly stated per-group n

@dataclass
class RawExtraction:
    """Direct LLM output. Strict extraction only — no inference.
    Every field that is not explicitly stated in the text must be null.
    Evidence strings are mandatory when the field is non-null.
    Per-field confidence reflects evidence directness, not overall extraction quality."""

    study_type:                  str            # free text, e.g. "prenatal developmental toxicity"
                                                # no controlled vocabulary — describe what you see

    route:                       Optional[list[str]]
    route_evidence:              Optional[str]
    route_confidence:            Optional[Literal["high","medium","low"]]  # null if route is null

    study_domain:                str            # §3.3 controlled vocab; 'general' if not determinable
    study_domain_evidence:       Optional[str]
    study_domain_confidence:     Optional[Literal["high","medium","low"]]

    procedure_text:              Optional[str]  # max 30 words; English
    procedure_text_evidence:     Optional[str]
    procedure_text_confidence:   Optional[Literal["high","medium","low"]]

    species:                     Optional[str]  # §3.4 controlled vocab
    species_evidence:            Optional[str]
    species_confidence:          Optional[Literal["high","medium","low"]]  # null if species is null

    animal_counts:               Optional[AnimalCounts]
    animal_counts_evidence:      Optional[str]  # single string covering all subfields
    animal_counts_confidence:    Optional[Literal["high","medium","low"]]  # null if animal_counts is null

    regulatory:                  Optional[bool]
    regulatory_evidence:         Optional[str]
    regulatory_confidence:       Optional[Literal["high","medium","low"]]  # null if regulatory is null

    notes:                       Optional[str]  # free-text; anything the structured
                                                # fields cannot represent; null if
                                                # nothing needs flagging

# ── Stage 2: application code output ─────────────────────────────────────────

@dataclass
class ExtractionResult:
    """Produced by ExtractionService after LLM call.
    endpoint_category is never written by the LLM."""

    raw:               RawExtraction
    endpoint_category: Optional[str]   # mapped from raw.study_type via §4.1 lookup;
                                        # null if study_type not in table

@dataclass
class AnalyzeResponse:
    experiments: list[ExtractionResult]  # min length 1; ordered by centrality to
                                          # stated objective / per-field confidence.
                                          # Phase 1: S2/S3 tabs for all experiments;
                                          # POST /search runs per experiment (ADR-019).
                                          # QueryRepository stores experiments[0]
                                          # only until Phase 2.
```

---

### 4.1 Lookup table — `study_type` → `endpoint_category`

Maintained here so Karynn can extend it alongside the methods database.
Matching is case-insensitive substring; first match wins.
If no row matches, `endpoint_category = null`.
Log all misses (the raw `study_type` string) — these are the primary signal for vocabulary expansion.

| study_type keywords (any match) | endpoint_category |
|---|---|
| acute toxicity, LD50, DL50, lethal dose, acute lethality, fixed dose procedure, acute toxic class, up-and-down procedure | `acute_toxicity` |
| skin irritation, dermal irritation, primary skin irritation | `skin_irritation` |
| skin corrosion, dermal corrosion, corrosivity | `skin_corrosion` |
| ocular irritation, eye irritation, draize eye, corneal irritation, conjunctival, EVEIT, ex vivo eye, BCOP | `ocular_irritation` |
| skin sensitisation, skin sensitization, contact sensitisation, allergic contact, LLNA, local lymph node | `skin_sensitisation` |
| phototoxicity, photoirritation, 3T3 NRU, photosensitization | `phototoxicity` |
| genotoxicity, mutagenicity, clastogenicity, chromosomal aberration, ames, bacterial reverse mutation, micronucleus, comet assay, DNA strand break, HPRT, gene mutation | `genotoxicity` |
| skin absorption, dermal absorption, percutaneous absorption, skin penetration | `skin_absorption` |
| reproductive toxicity, developmental toxicity, reproductive and developmental, prenatal developmental, two-generation reproductive, fertility, teratogenicity, embryo-fetal, combined screening | `reproductive_toxicity` |
| endocrine activity, endocrine disruption, estrogenic, androgenic, steroidogenic, estrogen receptor, androgen receptor | `endocrine_activity` |
| photoreactivity, photoreactive, reactive oxygen species, ROS generation | `photoreactivity` |
| aquatic toxicity, fish embryo, fish early life, FETAX, daphnia, algae growth | `aquatic_toxicity` |
| toxicokinetics, toxicokinetic, ADME, intrinsic clearance, metabolic clearance, hepatic clearance | `toxicokinetics` |
| bacterial endotoxin, endotoxin test, endotoxin activity, bacterial endotoxins, LAL test, LAL assay, BET assay, limulus amebocyte | `bacterial_endotoxin` |
| pyrogenicity, pyrogen, monocyte activation, MAT assay, rabbit pyrogen | `pyrogenicity` |
| rabies diagnosis, rabies virus, rabies antigen, rabies detection | `rabies_diagnosis` |

**Known misses from test set (null — vocabulary gaps):**
- "subchronic inhalation toxicity" → null
- "28-day repeated-dose oral toxicity" → null
- "photocarcinogenesis" → null
- "subacute oral toxicity" → null

---

### 4.2 Per-field confidence

Confidence is **per-field only**. Each `{field}_confidence` on `RawExtraction`
answers: *"how certain is this parameter value given the evidence for that
field?"* It is LLM-generated alongside the evidence string (see §9 prompt).

There is no overall or retrieval-level confidence on `ExtractionResult`.

**Per-field confidence scale (LLM-generated):**
- `"high"` — evidence is an explicit, direct statement requiring no interpretation (e.g., "p.o." → oral; "60 male Wistar rats" → rat, 60 males)
- `"medium"` — evidence requires vocabulary mapping or mild inference (e.g., "intragastric administration" → oral; "following OECD guidelines 414" → regulatory True)
- `"low"` — value extracted but evidence is tangential or required significant interpretation; user should verify
- `null` — field is null; confidence not applicable

**S2 display:**
- Per-field rows: `{field}_confidence` label (High / Medium / Low) on the left; "show evidence" toggle on the right (same row).
- Original protocol text shown in a side panel with evidence spans highlighted (ADR-018).
- When `len(experiments) > 1`: experiment tabs (labelled from each `study_type`) switch the active parameter set; user edits and searches from any tab.

**S3 display:**
- When `len(experiments) > 1`: matching experiment tabs; each tab shows that experiment's protocol summary, `notes`, and ranked recommendations.
- Result cards: 3Rs badge, **Match** score (%), jurisdiction, validation status, matched parameters, primary source link, OECD/regulatory link (includes `oecd_ref` when present, e.g. `OECD / regulatory (OECD TG 439)`).
- Cards with score ≤ 65% rendered at reduced opacity (ADR-011).

Threshold and per-field scale are first estimates — revisit after pilot using F11 relevance ratings.

---

O campo `notes` é exibido no S2 e no S3 (por aba de experimento) abaixo dos parâmetros extraídos.
Evidence fields são exibidos no S2 atrás de um toggle "ver evidência" por campo, alinhado à direita (ADR-016).
`study_type` e `endpoint_category` são exibidos juntos no S2 (ADR-015):
- `study_type`: o que o sistema identificou (texto livre do LLM)
- `endpoint_category`: o que o banco cobre ("Não coberto pelo banco" se null)
Quando `len(experiments) > 1`, S2 e S3 exibem abas por experimento (ADR-019) — não mais apenas um banner com o experimento principal.

---

## 5. Texto para embedding do protocolo

O embedding do protocolo (usado no cosine similarity) é gerado sobre:

```
{endpoint_category} {raw.procedure_text} {raw.study_domain}
```

Exemplo (protocolo do protótipo):
```
acute_toxicity Single-dose acute toxicity LD50 Litchfield-Wilcoxon oral intraperitoneal general
```

Regras:
- Campos `null` são omitidos
- `raw.route` é adicionado ao texto se não `null` (melhora similaridade com métodos de mesma via)
- `raw.species` NÃO é incluído no embedding (não deve influenciar o ranking)
- Sempre em inglês (todos os embeddings do banco são em inglês)
- `endpoint_category` vem de `ExtractionResult.endpoint_category` (pós-lookup), não do LLM

---

## 6. Regras de matching no RetrievalService

```
1. HARD FILTER: endpoint_category
   → Se protocol.endpoint_category is not None:
       incluir apenas methods WHERE endpoint_category = protocol.endpoint_category
   → Se None: sem filtro de endpoint (retorna todos; usuário corrigiu ou não corrigiu)

2. SOFT FILTER: route
   → Se protocol.route is not None:
       incluir methods WHERE (routes_applicable IS NULL
                              OR routes_applicable contém qualquer rota de protocol.route)
   → Se None: sem filtro de via

3. RANKING: cosine_similarity(protocol_embedding, method.embedding_json)
   → Calcular sobre os métodos que passaram nos filtros 1 e 2
   → Retornar todos, ordenados por score DESC
   → Frontend aplica opacidade para scores ≤ 65% (ADR-011)

4. MINIMUM RESULTS RULE:
   → Se resultado dos filtros < 3 métodos: relaxar filtro de route (manter só endpoint)
   → Se ainda < 3: retornar os 3 de maior score sem nenhum filtro
   → Registrar o relaxamento nos logs (para análise H3 no piloto)
```

A "Minimum Results Rule" garante o critério de sucesso do projeto:
"recebe ao menos 3 recomendações relevantes em menos de 60 segundos."

---

## 7. Exemplo completo — protocolo do protótipo

**Input:**
> "Bulgarian Plant Extract Toxicology (Wistar Rat) — Acute Toxicity (LD50) — Single-dose; Litchfield–Wilcoxon LD50; 60 male Wistar rats; p.o. / i.p.; up to 24h observation; LD50, mortality, clinical signs; Regulatory: Yes"

**AnalyzeResponse esperada:**
```python
AnalyzeResponse(experiments=[
    ExtractionResult(
        raw=RawExtraction(
            study_type          = "acute toxicity LD50 study",
            route               = ["oral", "intraperitoneal"],
            study_domain        = "general",
            procedure_text      = "Single-dose acute toxicity LD50 Litchfield-Wilcoxon",
            species             = "rat",
            animal_counts         = AnimalCounts(male=60),
            regulatory          = True,
            notes               = None,
        ),
        endpoint_category = "acute_toxicity",
    )
])
```

**Texto para embedding:**
```
acute_toxicity Single-dose acute toxicity LD50 Litchfield-Wilcoxon oral intraperitoneal general
```

**Filtros aplicados:**
1. endpoint_category = 'acute_toxicity' → retém: TG 420, 423, 425, GD 129
2. route contém 'oral' ou 'intraperitoneal' → todos os 4 passam (routes_applicable = ["oral"])

**Resultado esperado no S3:** TG 420, 423, 425, GD 129 — ordenados por cosine similarity.

---

## 8. Campos `routes_applicable` na tabela `methods` — valores por método

Para popular via UPDATE (ver `patch_routes.sql`):

| slug | routes_applicable |
|---|---|
| oecd-tg439-epiderm | `["dermal"]` |
| oecd-tg439-episkin | `["dermal"]` |
| oecd-tg431-rhe-corrosion | `["dermal"]` |
| oecd-tg430-ter-corrosion | `["dermal"]` |
| oecd-tg435-membrane-barrier | `["dermal"]` |
| oecd-tg437-bcop | `["ocular"]` |
| oecd-tg438-ice | `["ocular"]` |
| oecd-tg492-rce | `["ocular"]` |
| oecd-tg460-fluorescein-leakage | `["ocular"]` |
| oecd-tg442c-dpra | `["dermal"]` |
| oecd-tg442d-keratinosens | `["dermal"]` |
| oecd-tg442e-hclat | `["dermal"]` |
| oecd-tg429-llna | `["dermal"]` |
| oecd-tg442a-llna-da | `["dermal"]` |
| oecd-tg442b-llna-brdu | `["dermal"]` |
| oecd-tg432-3t3nru | `["dermal"]` |
| oecd-tg428-skin-absorption-vitro | `["dermal"]` |
| oecd-tg471-ames | `null` (in vitro, route-agnostic) |
| oecd-tg476-hprt | `null` |
| oecd-tg487-micronucleus | `null` |
| mat-monocyte-activation | `null` (detects contamination, route-agnostic) |
| niceatm-cytotox-basal-barranco | `["oral"]` |
| oecd-tg420-fixed-dose | `["oral"]` |
| oecd-tg423-atc | `["oral"]` |
| oecd-tg425-udp | `["oral"]` |

---

## 9. Prompt template para ExtractionService

> Manter neste documento; versionar com o código.
> Atualizado em ADR-014: array `experiments[]`; campo `notes`.
> Atualizado em ADR-015/016/017: two-stage output; evidence fields; structured animal_counts; strict extraction mode; synonym tables; splitting criteria.
> Atualizado em ADR-018: per-field `_confidence`; route ex vivo disambiguation; evidence length limits.

```
You are a scientific assistant specializing in animal research ethics.
Extract experimental parameters from the protocol description below.

STRICT EXTRACTION MODE: Extract only what is explicitly stated in the text.
Do not infer, assume, or use domain knowledge to fill gaps.
If a field is not explicitly stated, return null.
Use the notes field for any interpretation or likely inference.

CRITICAL: All _evidence fields must be short, exact quotes (maximum 15–20 words).
Do not quote entire paragraphs. Use the shortest phrase that supports the value.

── MULTI-EXPERIMENT SPLITTING ───────────────────────────────────────────────
Create a separate experiment object ONLY IF at least one of the following is true:
1. A different animal cohort is used (different group of animals — not the same
   animals measured at multiple timepoints or with multiple assays)
2. A materially different dosing regimen applies (different compound, different
   route, or different schedule — NOT different doses of the same compound)
3. A separate, explicitly-labelled study section describes an independent study
   (e.g. "Study 1", "Experiment 2", "Dose-range study")

Multiple assays on the same animals = one experiment object.
Multiple dose groups of the same compound = one experiment object.

── ROUTE SYNONYMS ───────────────────────────────────────────────────────────
CRITICAL: "route" describes how the test substance contacts the biological
system — NOT what type of biological system it is. For ex vivo preparations
(isolated corneas, skin discs, membrane models), choose the route that
describes substance-to-tissue contact, not the culture setup.

  ocular      ← instillation into eye, conjunctival, eye drop,
                  applied over cornea, applied to corneal surface,
                  applied to apex of cornea, ex vivo corneal application
                  (USE THIS for EVEIT, BCOP, ICE — even though they are
                  ex vivo systems, the substance contacts the corneal surface)

  dermal      ← topical, cutaneous, epicutaneous, skin application,
                  ex vivo skin disc, membrane model (Strat-M, Skin+)

  oral              ← p.o., gavage, gavagem, intragastric, intragástrico,
                       gastric tube, gastric intubation, dietary (mixed in feed)
  intraperitoneal   ← i.p.
  intravenous       ← i.v., endovenous
  inhalation        ← aerosol, nose-only chamber, inhalation chamber,
                       whole-body exposure
  null              ← UV irradiation, radiation, physical exposure,
                       or cell-culture medium exposure without an oriented tissue
                       surface (assay modality belongs in test_system, not route)
                       (radiation is not a chemical administration route)

── SPECIES SYNONYMS ─────────────────────────────────────────────────────────
  rat         ← Rattus norvegicus, Wistar, Sprague-Dawley, SD, F344, Fischer,
                  IGS, Crj:CD(SD), SKH (rat strain)
  mouse       ← Mus musculus, BALB/c, C57BL/6, SKH:HR1, hairless mouse
  rabbit      ← Oryctolagus cuniculus, New Zealand White
  guinea_pig  ← Cavia porcellus, cavie
  chicken     ← Gallus gallus
  zebrafish   ← Danio rerio
  in_vitro    ← cell culture, cell line, isolated cells
  other       ← any species not listed above (bovine, porcine, canine, etc.)

── OUTPUT FORMAT ────────────────────────────────────────────────────────────
Return ONLY valid JSON. No preamble. No markdown. No explanation outside JSON.
Your first character must be `{`. Do not write reasoning before the JSON object.
The JSON must be complete: close every string with a double quote and close
every object and array with } and ]. Never stop mid-field or mid-string.
Do NOT include a top-level "confidence" field. Confidence is per-field only —
each paired _confidence field reflects how directly that field's evidence
supports its value.

Per-field confidence scale:
  "high"   — evidence directly and explicitly states the value; no interpretation needed
  "medium" — evidence requires vocabulary mapping or mild inference
  "low"    — value extracted but evidence is tangential; user should verify
  null     — field is null; omit the confidence field

{
  "experiments": [
    {
      "study_type": "free-text description of the study type, e.g. 'prenatal
        developmental toxicity study' or 'in vivo genotoxicity battery'. Do not
        map to any controlled vocabulary here — describe what you see.",

      "route": array of controlled values (see synonyms above) or null,
      "route_evidence": "exact quote from text, MAX 15 WORDS" or null,
      "route_confidence": "high"|"medium"|"low" or null if route is null,

      "study_domain": one of [pharma, cosmetics, chemical_safety, general],
      "study_domain_evidence": "exact quote from text, MAX 15 WORDS" or null,
      "study_domain_confidence": "high"|"medium"|"low",
      // Use "general" when: (a) the study is validating a method rather than
      // testing a specific product class; (b) test substances span multiple
      // domains; (c) no single application domain is declared.
      // The identity of the test substance alone does not determine this field —
      // BAC is used in pharma, cosmetics, and industrial contexts equally.

      "procedure_text": "brief English description, max 30 words" or null,
      "procedure_text_evidence": "exact quote from text, MAX 20 WORDS" or null,
      "procedure_text_confidence": "high"|"medium"|"low" or null if procedure_text is null,

      "species": controlled value (see synonyms above) or null,
      "species_evidence": "exact quote from text, MAX 5 WORDS" or null,
      "species_confidence": "high"|"medium"|"low" or null if species is null,

      "animal_counts": {
        "female": integer (explicitly stated) or null,
        "male": integer (explicitly stated) or null,
        "total": integer (explicitly stated, not derived) or null,
        "per_group": integer (explicitly stated) or null
      } or null if no counts are explicitly stated,
      "animal_counts_evidence": "exact quote from text, MAX 15 WORDS" or null,
      "animal_counts_confidence": "high"|"medium"|"low" or null if animal_counts is null,

      "regulatory": true if a named regulatory guideline or authority is
        explicitly cited, false if explicitly stated as non-regulatory,
        null if not mentioned,
      "regulatory_evidence": "exact quote from text, MAX 20 WORDS" or null,
      "regulatory_confidence": "high"|"medium"|"low" or null if regulatory is null,

      "notes": "1-2 sentences on anything the structured fields cannot
        represent: secondary experiments, vocabulary gaps, ambiguous animal
        counts, unsupported routes, study designs outside the standard
        taxonomy, etc. null if nothing needs flagging."
    }
  ]
}

Order experiments by centrality to the protocol's stated objective,
or by per-field confidence if centrality is unclear.

CRITICAL: All _evidence fields must be short, exact quotes (maximum 15–20 words).
Do not quote entire paragraphs.

CRITICAL: Your response must be syntactically complete JSON. Close all strings,
objects, and arrays before ending output.

Protocol description:
{{protocol_text}}
```

---

## 10. Questão aberta para o piloto (H1 + H3)

O protótipo usou um input estruturado (tabela com campos explícitos).
O MVP usa free text.

**Teste mínimo antes de Phase 2:** Pedir a 3 pesquisadores que descrevam o protocolo
do exemplo acima em texto livre, sem ver a tabela. Verificar se `endpoint_category`,
`route` e `species` emergem naturalmente. Se não emergirem em ≥2/3 → ativar o
fallback de formulário estruturado (ver ADR-001 §13.6).

**Métrica adicional (adicionada após ADR-014):** Em cada sessão do piloto, registrar
se `len(experiments) > 1`. Se ≥2/5 sessões produzirem múltiplos experimentos, a UI
multi-experimento deve ser antecipada do Phase 3 para o Phase 2 — com deferimento
explícito de uma feature de peso equivalente (hard rule).

---

## 11. Exemplos reais — protocolos publicados (adicionados após ADR-014)

Estes exemplos são derivados de Materials & Methods de artigos publicados e
representam a forma como protocolos reais chegam ao sistema — não o input
sintético do §7. Usá-los como casos de teste para H3.

---

### 11.1 Carbon black — inhalação repetida (caso "sem cobertura")

**Fonte:** Seção Materials & Methods — estudo de exposição repetida a negro de fumo
por 90 dias em câmara nose-only.

**AnalyzeResponse esperada:**
```python
AnalyzeResponse(experiments=[
    ExtractionResult(
        raw=RawExtraction(
            study_type               = "subchronic inhalation toxicity study",
            route                    = ["inhalation"],
            route_evidence           = "exposed to CB in the nose-only inhalation chamber",
            study_domain             = "chemical_safety",
            study_domain_evidence    = "occupational exposure limit of 3.5 mg/m³ CB per 8 hrs work shift (established by OSHA and NIOSH)",
            procedure_text           = "90-day repeated-dose nose-only inhalation exposure to carbon black; lung function, histopathology, apoptosis, cytokine analysis",
            procedure_text_evidence  = "exposed to CB in the nose-only inhalation chamber at 30 mg/m³ for 6 hrs/day for 90 days",
            species                  = "rat",
            species_evidence         = "Male, pathogen-free Sprague–Dawley rats",
            animal_counts            = AnimalCounts(female=None, male=None, total=32, per_group=None),
            animal_counts_evidence   = "We divided 32 rats into two groups",
            regulatory               = None,
            regulatory_evidence      = None,
            notes                    = "No endpoint_category match: subchronic inhalation toxicity not in §3.1 vocabulary. Route 'inhalation' has no methods in MVP database. Protocol also includes a 14-day post-exposure recovery cohort not represented in any field."
        ),
        endpoint_category = None,   # "subchronic inhalation toxicity" not in §4.1 lookup
    )
])
```

**Comportamento esperado no S3:** Minimum Results Rule fires; 3 lowest-score methods, all ≤65% opacity (ADR-011).

---

### 11.2 Tanacetum parthenium EO — protocolo com dois experimentos distintos

**Fonte:** Seção Materials & Methods — estudo de LD50 (experimento 1) + estudo
subagudo 28 dias (experimento 2), publicados no mesmo artigo.

**AnalyzeResponse esperada:**
```python
AnalyzeResponse(experiments=[
    ExtractionResult(
        raw=RawExtraction(
            study_type               = "acute toxicity LD50 study",
            route                    = ["oral", "intraperitoneal"],
            route_evidence           = "administered a single dose of T. parthenium by two routes of administration—p.o. and i.p.",
            study_domain             = "general",
            study_domain_evidence    = None,
            procedure_text           = "Single-dose acute toxicity LD50 study by Litchfield-Wilcoxon method in Wistar rats, p.o. and i.p.",
            species                  = "rat",
            species_evidence         = "60 male Wistar rats",
            animal_counts            = AnimalCounts(female=None, male=60, total=None, per_group=None),
            animal_counts_evidence   = "A total of 60 male Wistar rats, equally divided into 10 groups",
            regulatory               = True,
            regulatory_evidence      = "Permission to use animals... obtained from the Food Safety Agency at the Bulgarian Ministry of Agriculture and Food... approved by the Ethical Committee... in accordance with the European Community Council directives: 86/609/EEC",
            notes                    = None
        ),
        endpoint_category = "acute_toxicity",
    ),
    ExtractionResult(
        raw=RawExtraction(
            study_type               = "28-day subacute repeated-dose oral toxicity study",
            route                    = ["oral"],
            route_evidence           = "treated once a day orally by gastric tube for 28 days",
            study_domain             = "general",
            study_domain_evidence    = None,
            procedure_text           = "28-day repeated-dose oral toxicity with hematological, serum biochemical, and histopathological evaluation",
            procedure_text_evidence  = "treated once a day orally by gastric tube for 28 days... blood samples were drawn for the examination of hematological and serum biochemical parameters",
            species                  = "rat",
            species_evidence         = "20 white male Wistar rats",
            animal_counts            = AnimalCounts(female=None, male=20, total=None, per_group=10),
            animal_counts_evidence   = "20 white male Wistar rats... divided into two groups of 10 animals",
            regulatory               = True,
            regulatory_evidence      = "Permission to use animals... obtained from the Food Safety Agency at the Bulgarian Ministry of Agriculture and Food",
            notes                    = "28-day repeated-dose design (OECD TG 407-class); not in §4.1 lookup; no method match possible in MVP database."
        ),
        endpoint_category = None,
    )
])
```

**Comportamento esperado no S2:**
- Abas por experimento (acute LD50 | subacute 28-day).
- Cada aba: params editáveis, evidence toggles, `notes` do experimento ativo.

**Comportamento esperado no S3:**
- Mesmas abas; busca dispara `POST /search` para **todos** os experimentos em paralelo ao confirmar no S2.
- Aba acute: TG 420, 423, 425, GD 129 ordenados por score.
- Aba subacute: `endpoint_category = null` → estado vazio "Não coberto pelo banco".

---

### 11.3 EVEIT — sistema ex vivo (caso de disambiguação de rota e study_domain)

**Fonte:** Materials & Methods do EVEIT (Ex Vivo Eye Irritation Test) usando córneas
bovinas de abatedouro.

**Casos de falha conhecidos em outros modelos:**
- `route: in_vitro` (errado) em vez de `ocular` — o sistema ex vivo não determina a rota; a rota é o contato da substância com o tecido. Ver §3.2 tabela de disambiguação.
- `study_domain: cosmetics` (errado) em vez de `general` — BAC presente no texto não determina `cosmetics`. Ver §3.3 regra para estudos de validação de método.
- top-level `confidence` na saída do LLM (errado) — proibido; usar `{field}_confidence` por campo (ADR-018).

**AnalyzeResponse esperada:**
```python
AnalyzeResponse(experiments=[
    ExtractionResult(
        raw=RawExtraction(
            study_type               = "ex vivo eye irritation test (EVEIT) using bovine corneas",
            route                    = ["ocular"],
            route_evidence           = "A 20µl drop of each solution was applied exactly over the apex of the cornea",
            route_confidence         = "high",
            # route = "ocular" because the test substance contacts the corneal
            # surface. The perfusion chamber / MEM medium is the biological system,
            # not the route. See §3.2 ex vivo disambiguation table.
            study_domain             = "general",
            study_domain_evidence    = None,
            study_domain_confidence  = "medium",
            # study_domain = "general" because: (a) the study characterizes
            # the EVEIT method itself, not a product class; (b) test substances
            # span pharma (HYLO-LASOP), preservative (BAC), and saline control.
            # BAC's presence alone does not imply cosmetics. See §3.3 rule 1.
            # evidence = None because "general" follows from rule, not explicit text.
            # confidence = "medium" because classification requires interpretation.
            procedure_text           = "Ex vivo bovine cornea perfusion (EVEIT); hourly topical application; fluorescein staining, lactate, glucose, pH monitoring",
            procedure_text_evidence  = "A 20µl drop of each solution was applied hourly... All defects were stained daily with fluorescein",
            procedure_text_confidence= "high",
            species                  = "other",
            species_evidence         = "corneas that are freshly-obtained from the slaughter house",
            species_confidence       = "medium",
            # species = "other": bovine not in §3.4. Do NOT use "in_vitro" —
            # this is ex vivo intact tissue, not a cell culture.
            # confidence = "medium": "other" requires inference that these are
            # bovine corneas; species not named explicitly.
            animal_counts            = None,
            animal_counts_evidence   = None,
            animal_counts_confidence = None,
            # animal_counts = None: corneas are slaughterhouse byproducts.
            # No experimental animal cohort exists; count is not meaningful.
            regulatory               = None,
            regulatory_evidence      = None,
            regulatory_confidence    = None,
            notes                    = "EVEIT (Ex Vivo Eye Irritation Test) using post-slaughter bovine corneas — an alternative to the Draize rabbit eye test. Species is bovine, mapped to 'other'. animal_counts is null: corneas are slaughterhouse byproducts, not experimental animals. Returning ocular_irritation recommendations (TG 437/438/460) is correct behavior."
        ),
        endpoint_category = "ocular_irritation",
    )
])
```

**Comportamento esperado no S3:** TG 437 (BCOP), TG 438 (ICE), TG 460 (Fluorescein Leakage) — ordenados por cosine similarity. Resultado correto: o pesquisador está usando um método ex vivo e o sistema retorna métodos validados comparáveis.
