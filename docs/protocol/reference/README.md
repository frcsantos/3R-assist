# Basket 1 / Stratum B — LLM reference extraction (draft, not expert-validated)

Generated 2026-11-20 from the 16 `include_proposed` Stratum B articles.

- `raw/<PMID>.claude-opus-4.8.raw.json` — reference candidate (Anthropic Claude Opus 4.8 via OpenRouter `anthropic/claude-opus-4.8`).
- `raw/<PMID>.gpt-6.2-sol.raw.json` — cross-check (OpenAI GPT-6.2 Sol via OpenRouter `openai/gpt-6.2-sol`).
- `input_text/<PMID>.input.txt` — exact text sent to the models (GROBID Methods + legends, or pypdf fallback).
- `disagreement_sheet.csv` — field-level comparison (Opus 4.8 = reference candidate; Sol 6.2; Gemini 3.1 Flash Lite runs 1 and 2) for expert adjudication; fill `expert_value` / `expert_notes`.

Provenance and caveats:
- Prompt: `build_extraction_prompt` from the working tree on 2026-11-20 (uncommitted P2 rewrite), with the vocabulary loaded from the database (58 endpoint slugs, 21 routes, 17 species).
- Single run per model, max_tokens 16000 (Sol: 40000 for 36456880 and 39999211). Outputs are not deterministic; no stability runs yet (§7).
- Agreement between models is not correctness. Both models over-split articles into many experiments; the pilot needs one selected procedure per article.
- Claude Opus 5.5 was tried first and rejected: OpenRouter returned `content_filter` for 7 of 16 articles, deterministically.
- Evidence quotes were fuzzy-checked against `input_text` (Opus 97%, Sol 100% found).

## Stability / production-model runs (raw_stability/)
- `*.gemini-3.1-flash-lite.r1|r2.raw.json` — two runs of the production model (`google/gemini-3.1-flash-lite`), same prompt and texts, max_tokens 40000.
- `*.claude-opus-4.8.r2|r3.raw.json` — INCOMPLETE (2 and 1 of 16 files): OpenRouter returned 402 (in-flight budget) after credits ran low (~$1.39 left of $20). Opus 4.8 stability is not measured yet.
