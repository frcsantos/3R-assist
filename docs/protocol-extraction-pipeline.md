# Protocol Parameter Extraction from Article PDFs

Design notes for extracting experimental parameters from scientific article PDFs with a low-cost LLM.

## 1. Problem

- Whole-article text is too long for a cheap model to process reliably. Extraction quality also drops on long inputs even when they fit in the context window (the "lost in the middle" effect).
- Naive PDF text extraction scrambles or truncates lines. Two-column layouts get read across columns, headers, footers and line numbers leak in, and words hyphenated at line breaks get split.

## 2. Strategy at a glance

1. **Parse** the PDF with a layout-aware, science-specific parser (GROBID). This fixes reading order and returns labelled sections.
2. **Isolate** the Methods section, plus figure legends and tables, which often hold doses, *n* and timepoints.
3. **Extract** with a cheap LLM (pass 1) on that short context, using a JSON schema, explicit `null`s and a verbatim evidence quote for each field.
4. **Fill gaps** (pass 2): for fields still `null`, retrieve the top paragraphs from the rest of the paper with BM25 and re-ask only for those fields.
5. **Verify** each value by fuzzy-matching its evidence quote against the source text.
6. **Evaluate** against a small hand-annotated gold set before tuning anything.

```
PDF ──► GROBID (CRF) ──► TEI XML ──► sections
                                       │
               ┌───────────────────────┴──────────────┐
               ▼                                      ▼
   Methods + legends + tables               all other paragraphs
               │                                      │
               ▼                                      │
     LLM pass 1 (JSON + evidence)                     │
               │ null fields                          │
               └────────► BM25 top-k ◄────────────────┘
                              │
                              ▼
                 LLM pass 2 (missing fields only)
                              │
                              ▼
               evidence verification ──► output / review queue
```

## 3. Parser: GROBID

**Why GROBID:** it is built for scientific articles, outputs TEI XML with sections, figure legends and references already separated, and runs on CPU in CRF mode (no GPU, no PyTorch). It is licensed Apache 2.0, so there are no restrictions on nonprofit or commercial use.

### 3.1 Hosting plan

| Phase | Where GROBID runs | Notes |
|---|---|---|
| **Now: prototyping** | GROBID public demo server | Free. Quota-limited, no uptime guarantee, PDFs are sent to a third party. Only for testing and public papers. |
| **Now: light production** | Our own Hugging Face Space (duplicate of an official GROBID Space) | Free CPU tier is enough for CRF mode. Free Spaces sleep when idle, so expect a cold start of about a minute. Set the Space to **private** if any PDFs are unpublished. |
| **Later, if needed** | Google Cloud Run / Render / Fly.io with the CRF Docker image | Use if cold starts or volume become a problem. Give it at least 2–4 GB RAM. |

The GROBID URL is an environment variable (`GROBID_URL`), so switching phases requires no code change.

**Setting up the HF Space:**
1. Open an official GROBID Space on Hugging Face (e.g. under the `lfoppiano` or `grobidOrg` accounts; prefer a CRF-only image).
2. Click **⋮ → Duplicate this Space**. Choose our org, set visibility (private if needed) and keep the free CPU hardware.
3. Wait for the build, then set `GROBID_URL=https://<our-org>-<space-name>.hf.space`.
4. Check it's running: `GET {GROBID_URL}/api/isalive` should return `true`.
5. For a private Space, send a Hugging Face token: `Authorization: Bearer <HF_TOKEN>`.

> Before going live, verify the current demo URL and image tags on the GROBID docs and GitHub. They change between releases.

### 3.2 Known limitations of CRF mode
- Tables come out as flattened text. If key parameters live mainly in tables, add a Docling step for table pages (OCR off; small CPU model).
- Scanned PDFs return little or no text. Detect them (see §5.3) and route them to a review queue instead of parsing.
- Accuracy on unusual layouts is somewhat lower than in GROBID's deep-learning mode. Measure this on the gold set (§8).

## 4. Getting the Methods text

```python
import os
import re
import requests
from lxml import etree

GROBID_URL = os.environ.get("GROBID_URL", "http://localhost:8070")
HF_TOKEN = os.environ.get("HF_TOKEN")  # only for private Spaces
NS = {"tei": "http://www.tei-c.org/ns/1.0"}

METHOD_KEYS = (
    "method", "materials", "experimental", "procedure", "protocol",
    "study design", "animals", "subjects", "participants", "star",
)
STOP_KEYS = ("result", "discussion", "conclusion", "acknowledg", "reference")


def grobid_parse(pdf_path: str, timeout: int = 180) -> etree._Element:
    headers = {"Authorization": f"Bearer {HF_TOKEN}"} if HF_TOKEN else {}
    with open(pdf_path, "rb") as f:
        r = requests.post(
            f"{GROBID_URL}/api/processFulltextDocument",
            files={"input": f},
            data={"consolidateHeader": "0", "consolidateCitations": "0"},
            headers=headers,
            timeout=timeout,  # generous: HF Space cold starts
        )
    r.raise_for_status()
    return etree.fromstring(r.content)


def _text(el) -> str:
    return re.sub(r"\s+", " ", "".join(el.itertext())).strip()


def get_sections(tei) -> list[tuple[str, list[str]]]:
    """[(heading, [paragraph, ...]), ...] in document order."""
    out = []
    for div in tei.iterfind(".//tei:body/tei:div", NS):
        head = div.findtext("tei:head", default="", namespaces=NS).strip()
        paras = [_text(p) for p in div.iterfind("tei:p", NS)]
        out.append((head, [p for p in paras if p]))
    return out


def get_legends_and_tables(tei) -> list[str]:
    items = []
    for fig in tei.iterfind(".//tei:figure", NS):
        head = fig.findtext("tei:head", default="", namespaces=NS)
        desc = fig.find("tei:figDesc", NS)
        table = fig.find("tei:table", NS)
        parts = [head]
        if desc is not None:
            parts.append(_text(desc))
        if table is not None:
            parts.append(_text(table))
        txt = " ".join(p for p in parts if p).strip()
        if txt:
            items.append(txt)
    return items


def split_methods(sections):
    """Return (methods_paragraphs, other_paragraphs).

    GROBID often emits Methods subsections ('Animals', 'Drug administration')
    as separate top-level divs, so we stay 'inside' until a stop heading.
    """
    methods, other, inside = [], [], False
    for head, paras in sections:
        h = head.lower()
        if any(k in h for k in METHOD_KEYS):
            inside = True
        elif inside and any(k in h for k in STOP_KEYS):
            inside = False
        target = methods if inside else other
        target.extend(f"[{head}] {p}" if head else p for p in paras)
    return methods, other
```

If `methods` comes back empty (no recognizable heading), skip pass 1 and go straight to retrieval over the whole paper (§6) for all fields.

## 5. Cleaning and guards

### 5.1 Text normalization
GROBID already handles reading order and most hyphenation. Apply light cleaning on top:

```python
import unicodedata

def clean(text: str) -> str:
    text = unicodedata.normalize("NFKC", text)            # ligatures: ﬁ -> fi
    text = re.sub(r"(\w)-\s+(\w)", r"\1\2", text)          # residual hyphenation
    return re.sub(r"\s+", " ", text).strip()
```

There is no line-number stripping here on purpose. Add a targeted rule only if the gold set shows line numbers leaking from preprint PDFs, because a naive rule can delete real numbers.

### 5.2 Token budget
- Target **≤ 4–6k input tokens per call** for the cheap model.
- If Methods + legends exceed the budget, split by subsection and run pass 1 per chunk, then merge (§7.2).

### 5.3 Scanned-PDF detection
If the total extracted characters divided by the page count is below ~200, treat the PDF as scanned or broken. Mark it `needs_ocr` and send it to the review queue rather than letting the LLM guess.

## 6. LLM extraction

### 6.1 Output schema (example; adapt fields)

Each field returns a value, a verbatim evidence quote and a status:

```json
{
  "species":        {"value": "Wistar rats", "evidence": "Male Wistar rats (250–300 g) were ...", "status": "found"},
  "sex":            {"value": "male", "evidence": "Male Wistar rats ...", "status": "found"},
  "n_per_group":    {"value": null, "evidence": null, "status": "not_found"},
  "dose":           {"value": "10 mg/kg", "evidence": "... at 10 mg/kg i.p. ...", "status": "found"},
  "route":          {"value": "intraperitoneal", "evidence": "... i.p. ...", "status": "found"},
  "duration":       {"value": null, "evidence": null, "status": "referenced_elsewhere"}
}
```

`status` values:
- `found`: the value is stated in the text given.
- `not_found`: the value is not in the text given.
- `referenced_elsewhere`: the text says "as previously described [ref]" or "see Supplementary". Flag these for humans; retrieval cannot fix them.

### 6.2 Prompt rules for cheap models
- Ask for **one parameter group per call** (e.g. subjects / intervention / outcomes) rather than one large schema. Cheap models drop fields from big schemas.
- State: *"Use only the text provided. If a value is not explicitly stated, return null with status not_found. Do not infer or compute values."*
- **Require the evidence to be copied verbatim** from the text, as one contiguous span.
- Use the provider's structured-output / JSON-schema mode where available.
- Temperature 0.
- Normalize units **in code** after extraction, not in the prompt.

### 6.3 Pass 1: Methods context
Input is the cleaned Methods paragraphs plus figure legends and table text. Run once per parameter group.

### 6.4 Pass 2: retrieval for missing fields
Only for fields with `status == "not_found"`:

```python
from rank_bm25 import BM25Okapi

FIELD_QUERIES = {
    "n_per_group": ["n =", "per group", "animals per", "subjects", "sample size"],
    "dose":        ["mg/kg", "dose", "µg", "administered", "concentration"],
    "duration":    ["days", "weeks", "for", "period", "treatment lasted"],
    # ... one entry per field
}

def retrieve(paragraphs: list[str], field: str, k: int = 4) -> list[str]:
    tokenized = [p.lower().split() for p in paragraphs]
    bm25 = BM25Okapi(tokenized)
    query = " ".join(FIELD_QUERIES[field]).lower().split()
    scores = bm25.get_scores(query)
    ranked = sorted(range(len(paragraphs)), key=lambda i: scores[i], reverse=True)
    return [paragraphs[i] for i in ranked[:k]]
```

Search over `other` paragraphs from `split_methods` (plus the abstract). Combine the retrieved paragraphs for all missing fields (deduplicated), then make one LLM call that asks only for those fields. Add embeddings only if the gold set shows BM25 recall is poor.

## 7. Verification and merging

### 7.1 Evidence check (main guard against made-up values)

```python
from rapidfuzz import fuzz

def verify(field_result: dict, source_text: str, threshold: int = 90) -> dict:
    ev = field_result.get("evidence")
    if field_result.get("status") != "found" or not ev:
        return field_result
    score = fuzz.partial_ratio(ev.lower(), source_text.lower())
    field_result["evidence_score"] = score
    if score < threshold:
        field_result["status"] = "unverified"   # route to review
    elif field_result["value"] and not value_in_evidence(field_result["value"], ev):
        field_result["status"] = "value_not_in_evidence"
    return field_result

def value_in_evidence(value: str, evidence: str) -> bool:
    # numbers in the value must appear in the evidence
    nums = re.findall(r"\d+(?:[.,]\d+)?", str(value))
    return all(n in evidence for n in nums)
```

### 7.2 Merging chunked or multi-pass results
- Keep the first `found` and verified value. Pass 1 (Methods) wins over pass 2 (retrieval).
- If two verified values conflict (e.g. different doses for different groups), keep both and mark `status = "conflict"`. Multiple groups are common and should not be collapsed silently.

### 7.3 Output record
For each paper, store: the parameter values with status and evidence, the GROBID version, the LLM model and prompt version, and which pass produced each value. This makes re-runs and audits possible.

## 8. Evaluation (do this before tuning)

1. **Gold set:** hand-annotate 30–50 papers covering the main journals and layouts, including some two-column, some with Methods at the end, some preprints and at least a few with "as previously described".
2. **Compare configurations**, per field:
   - A: Methods only (pass 1)
   - B: Methods + retrieval (pass 1 + pass 2)
   - C: whole paper with a stronger model (the upper bound)
3. **Metrics per field:** exact/normalized match accuracy, rate of wrong `null`s, and rate of values that are present but wrong (the costly error).
4. **Read the failures** and label each one: parser error, section-detection error, retrieval miss, or LLM error. Fix the largest category first.

## 9. Edge cases checklist

| Case | Handling |
|---|---|
| Methods at end of paper (Nature-style, "Online Methods") | Heading match still works, because it doesn't depend on position. |
| Cell "STAR Methods" | `"star"` is in `METHOD_KEYS`; check on the gold set. |
| No recognizable Methods heading | Retrieval over the whole paper for all fields. |
| Values only in figure legends or tables | Legends and table text are always included in pass 1. |
| "As previously described [12]" | `status = referenced_elsewhere`, sent to human review. |
| Supplementary methods | Out of scope for now; flag and record whether a supplement exists. |
| Scanned PDF | Character-density check gives `needs_ocr` and sends it to review. |
| Multiple experiments or groups | Allow lists in the schema; conflicts get `status = "conflict"`. |
| HF Space asleep | Long timeout (≥ 180 s) plus one retry with backoff. |
| Demo server quota exceeded | Prototyping only; switch `GROBID_URL` to our Space. |

## 10. Dependencies and licenses

| Component | License | Notes |
|---|---|---|
| GROBID | Apache 2.0 | It calls a GPL binary (pdfalto) as an external program; the maintainers consider this fine. |
| Docling (optional, tables) | MIT | Check the model licenses in `docling-ibm-models`. |
| `rank_bm25` | Apache 2.0 | |
| `rapidfuzz` | MIT | |
| `lxml`, `requests` | BSD / Apache 2.0 | |

Avoid PyMuPDF (AGPL) in a hosted service unless the backend is open source. Marker's model weights have a revenue-gated license and the models are heavier than this pipeline needs.

## 11. Next steps

1. Run the parser and Methods split against the public demo on 10 sample PDFs and inspect the TEI output by hand.
2. Duplicate the GROBID Space into our org (private if needed) and switch `GROBID_URL`.
3. Define the final parameter schema and the field groups.
4. Build the gold set (30–50 papers).
5. Implement pass 1 and verification, then measure config A.
6. Add pass 2 (BM25), then measure config B and compare.
7. Decide on the Docling table step based on how many errors come from tables.
8. Set up the human-review queue for `unverified`, `conflict`, `referenced_elsewhere` and `needs_ocr`.

## 12. Open questions

- Are any input PDFs confidential (unpublished protocols)? If yes, the demo server is ruled out for them and the Space must be private.
- What share of target parameters live in tables rather than running text?
- Expected volume (PDFs per day)? This decides whether the free Space is enough.
