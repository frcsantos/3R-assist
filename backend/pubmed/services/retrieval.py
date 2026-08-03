"""Two-path retrieval service.

Path A — Endpoint search
  Embeds a neutral description of the scientific endpoint/hypothesis and searches
  for any paper studying that outcome, regardless of methodology. The LLM ranker
  later classifies each result by 3R class.

Path B — Reconstruction search
  The LLM proposes one concrete alternative per 3R class. Each proposal is
  embedded and searched independently. Replacement queries get more candidates
  than reduction, which gets more than refinement, biasing discovery before
  the ranking step even runs.

Results from both paths are merged by PMID (keeping the highest cosine score),
then the LLM ranker filters and re-ranks using 3R weights:
  replacement × 1.00 > reduction × 0.65 > refinement × 0.35
"""

from __future__ import annotations

import asyncio
import json
import logging
from dataclasses import dataclass, field

from app.adapters.embedder import EmbedderAdapter
from app.adapters.llm import LLMAdapter
from app.models.protocol import ProtocolParameters
from pubmed.db.repository import PubMedRepository
from pubmed.models.analysis import Citation, LLMProposedAlternative, PubMedRecommendation
from pubmed.models.record import Author, PubMedRecord
from pubmed.prompts.alternative_query import build_alternative_query_prompt
from pubmed.prompts.ranking import build_ranking_prompt
from pubmed.prompts.study_summary import build_study_summary_prompt
from pubmed.prompts.summary import build_summary_prompt

logger = logging.getLogger(__name__)

# How many vector-search candidates each query retrieves.
# Replacement gets the most — biases the candidate pool before scoring.
TOP_K_ENDPOINT = 12
TOP_K_BY_CLASS: dict[str, int] = {
    "replacement": 15,
    "reduction":   10,
    "refinement":   5,
}

# Final score = cosine × weight. Replace stays at 1.0 so a strong replacement
# always beats an equal-cosine reduction or refinement.
THREE_R_WEIGHTS: dict[str, float] = {
    "replacement": 1.00,
    "reduction":   0.65,
    "refinement":  0.35,
}

_PLAN_MAX_TOKENS = 512
_RANK_MAX_TOKENS = 1024
_SUMMARY_MAX_TOKENS = 256
_CANDIDATES_FOR_LLM = 10  # max candidates passed to the ranking LLM
_ABSTRACT_CHAR_LIMIT = 400  # truncate abstracts sent to LLM to keep prompts short
_MIN_COSINE_FALLBACK = 0.5  # if LLM includes nothing, return candidates above this score


@dataclass
class _Candidate:
    record: PubMedRecord
    cosine: float
    source_class: str | None = None   # three_r_class from whichever path found it first


@dataclass
class StudySummary:
    scientific_question: str
    endpoint_description: str
    current_method: str


@dataclass
class SearchPlan:
    endpoint_hypothesis: str
    endpoint_search_query: str
    alternatives: list[LLMProposedAlternative] = field(default_factory=list)


class PubMedRetrievalService:
    def __init__(
        self,
        repository: PubMedRepository,
        embedder: EmbedderAdapter,
        llm: LLMAdapter,
    ) -> None:
        self._repository = repository
        self._embedder = embedder
        self._llm = llm

    # ──────────────────────────────────────────────────────────────────────────
    # Public interface
    # ──────────────────────────────────────────────────────────────────────────

    async def search(
        self,
        params: ProtocolParameters,
        protocol_text: str,
    ) -> tuple[list[PubMedRecommendation], str | None, int]:
        """
        Returns:
            recommendations     — literature-backed results, ranked and filtered
            endpoint_hypothesis — the LLM's understanding of what is being tested
            total_candidates    — number of unique papers evaluated

        LLM-proposed alternatives are used internally as Path B search queries
        and are never surfaced in the response (to avoid hallucinations).
        """
        plan = self._generate_search_plan(protocol_text, params)

        # Run both paths concurrently
        path_a_task = asyncio.create_task(
            self._path_a_endpoint(plan.endpoint_search_query)
        )
        path_b_task = asyncio.create_task(
            self._path_b_reconstruction(plan.alternatives)
        )
        path_a_results, path_b_results = await asyncio.gather(path_a_task, path_b_task)

        # Merge: keep the highest cosine per PMID
        merged: dict[str, _Candidate] = {}
        for candidate in path_a_results + path_b_results:
            existing = merged.get(candidate.record.pmid)
            if existing is None or candidate.cosine > existing.cosine:
                merged[candidate.record.pmid] = candidate

        total_candidates = len(merged)
        if not merged:
            return [], plan.endpoint_hypothesis, 0

        # Sort by cosine descending and pass the top slice to the LLM ranker
        sorted_candidates = sorted(merged.values(), key=lambda c: -c.cosine)
        llm_input = [
            {
                "pmid": c.record.pmid,
                "title": c.record.title,
                "abstract_text": (c.record.abstract_text or "")[:_ABSTRACT_CHAR_LIMIT],
                "source_class": c.source_class,
            }
            for c in sorted_candidates[:_CANDIDATES_FOR_LLM]
        ]

        record_by_pmid = {c.record.pmid: c.record for c in sorted_candidates}
        cosine_by_pmid = {c.record.pmid: c.cosine for c in sorted_candidates}

        ranked_meta = self._rank_with_llm(params, llm_input)
        if ranked_meta:
            recommendations = self._build_recommendations(
                ranked_meta, record_by_pmid, cosine_by_pmid
            )
            if recommendations:
                return recommendations, plan.endpoint_hypothesis, total_candidates

        # LLM unavailable or filtered everything out — return top candidates by cosine
        logger.info(
            "LLM ranking returned no results; falling back to cosine-only top candidates"
        )
        fallback_recs = self._build_cosine_fallback(sorted_candidates)
        return fallback_recs, plan.endpoint_hypothesis, total_candidates

    # ──────────────────────────────────────────────────────────────────────────
    # Path A — endpoint/hypothesis search
    # ──────────────────────────────────────────────────────────────────────────

    async def _path_a_endpoint(self, endpoint_query: str) -> list[_Candidate]:
        """Search endpoint_embedding column — finds papers studying the same phenomenon."""
        embedding = await asyncio.get_event_loop().run_in_executor(
            None, self._embedder.embed, endpoint_query
        )
        rows = await self._repository.search_by_endpoint_embedding(
            embedding, top_k=TOP_K_ENDPOINT
        )
        return [_Candidate(record=rec, cosine=score, source_class=None) for rec, score in rows]

    # ──────────────────────────────────────────────────────────────────────────
    # Path B — reconstruction search (one query per 3R class)
    # ──────────────────────────────────────────────────────────────────────────

    async def _path_b_reconstruction(
        self, alternatives: list[LLMProposedAlternative]
    ) -> list[_Candidate]:
        tasks = [self._search_single_alternative(alt) for alt in alternatives]
        results = await asyncio.gather(*tasks)
        return [c for batch in results for c in batch]

    async def _search_single_alternative(
        self, alt: LLMProposedAlternative
    ) -> list[_Candidate]:
        """Search method_embedding column — finds papers describing similar techniques."""
        top_k = TOP_K_BY_CLASS.get(alt.three_r_class, 5)
        embedding = await asyncio.get_event_loop().run_in_executor(
            None, self._embedder.embed, alt.method_description
        )
        rows = await self._repository.search_by_method_embedding(
            embedding, top_k=top_k
        )
        return [
            _Candidate(record=rec, cosine=score, source_class=alt.three_r_class)
            for rec, score in rows
        ]

    # ──────────────────────────────────────────────────────────────────────────
    # LLM-based ranking and filtering
    # ──────────────────────────────────────────────────────────────────────────

    def _rank_with_llm(
        self, params: ProtocolParameters, candidates: list[dict]
    ) -> list[dict] | None:
        prompt = build_ranking_prompt(
            endpoint_category=params.endpoint_category,
            study_domain=params.study_domain,
            procedure_text=params.procedure_text,
            candidates=candidates,
        )
        raw = self._llm.call(prompt, max_tokens=_RANK_MAX_TOKENS, json_mode=True)
        if raw is None:
            logger.warning("LLM ranking unavailable — no model configured or call failed")
            return None
        try:
            return json.loads(raw).get("ranked", [])
        except (json.JSONDecodeError, AttributeError) as exc:
            logger.warning("LLM ranking parse error: %s", exc)
            return None

    # ──────────────────────────────────────────────────────────────────────────
    # Build final recommendations applying 3R weights
    # ──────────────────────────────────────────────────────────────────────────

    @staticmethod
    def _build_recommendations(
        ranked_meta: list[dict],
        record_by_pmid: dict[str, PubMedRecord],
        cosine_by_pmid: dict[str, float],
    ) -> list[PubMedRecommendation]:
        scored: list[tuple[PubMedRecord, float, dict]] = []
        for item in ranked_meta:
            if not item.get("include", False):
                continue
            pmid = item.get("pmid", "")
            record = record_by_pmid.get(pmid)
            if record is None:
                continue
            three_r = item.get("three_r_class", "refinement")
            if three_r not in THREE_R_WEIGHTS:
                three_r = "refinement"
            cosine = cosine_by_pmid.get(pmid, 0.0)
            weighted = round(cosine * THREE_R_WEIGHTS[three_r], 4)
            scored.append((record, weighted, item))

        scored.sort(key=lambda x: -x[1])

        return [
            PubMedRecommendation(
                record=record,
                relevance_score=weighted,
                relevance_explanation=meta.get("relevance_explanation", ""),
                three_r_class=meta.get("three_r_class", "refinement"),
                endpoint_category=meta.get("endpoint_category") or None,
                rank=rank,
            )
            for rank, (record, weighted, meta) in enumerate(scored, start=1)
        ]

    @staticmethod
    def _build_cosine_fallback(
        sorted_candidates: list[_Candidate],
    ) -> list[PubMedRecommendation]:
        """Return top candidates by cosine score when LLM ranking produces nothing."""
        results = []
        for rank, c in enumerate(sorted_candidates[:_CANDIDATES_FOR_LLM], start=1):
            if c.cosine < _MIN_COSINE_FALLBACK:
                break
            three_r = c.source_class or "refinement"
            weighted = round(c.cosine * THREE_R_WEIGHTS.get(three_r, 0.35), 4)
            results.append(
                PubMedRecommendation(
                    record=c.record,
                    relevance_score=weighted,
                    relevance_explanation="Selected by semantic similarity to the study endpoint.",
                    three_r_class=three_r,
                    endpoint_category=None,
                    rank=rank,
                )
            )
        return results

    # ──────────────────────────────────────────────────────────────────────────
    # Post-ranking synthesis: summary + citations
    # ──────────────────────────────────────────────────────────────────────────

    def generate_summary(
        self,
        params: ProtocolParameters,
        recommendations: list[PubMedRecommendation],
    ) -> tuple[str | None, list[Citation]]:
        """
        Returns (summary_text, citations).
        Citations are built from records already in `recommendations` — the LLM
        only selects which PMIDs to cite; bibliographic fields are never model-generated.
        """
        if not recommendations:
            return None, []

        llm_input = [
            {
                "pmid": r.record.pmid,
                "title": r.record.title,
                "abstract_text": (r.record.abstract_text or "")[:_ABSTRACT_CHAR_LIMIT],
                "three_r_class": r.three_r_class,
                "relevance_explanation": r.relevance_explanation,
                "rank": r.rank,
            }
            for r in recommendations
        ]

        prompt = build_summary_prompt(
            endpoint_category=params.endpoint_category,
            study_domain=params.study_domain,
            procedure_text=params.procedure_text,
            recommendations=llm_input,
        )

        raw = self._llm.call(prompt, max_tokens=_SUMMARY_MAX_TOKENS, json_mode=True)
        if raw is None:
            logger.warning("Summary LLM unavailable — no model configured or call failed")
            return None, []

        try:
            payload = json.loads(raw)
        except (json.JSONDecodeError, AttributeError) as exc:
            logger.warning("Summary parse error: %s", exc)
            return None, []

        summary = payload.get("summary") or None
        cited_pmids: list[str] = payload.get("cited_pmids") or []

        record_by_pmid = {r.record.pmid: r.record for r in recommendations}
        citations = [
            self._build_citation(record_by_pmid[pmid])
            for pmid in cited_pmids
            if pmid in record_by_pmid
        ]

        return summary, citations

    @staticmethod
    def _build_citation(record: PubMedRecord) -> Citation:
        names = [
            a.display_name
            for a in record.authors
            if a.display_name != "Unknown"
        ]
        if len(names) <= 3:
            authors_display = ", ".join(names) if names else "Unknown authors"
        else:
            authors_display = ", ".join(names[:3]) + " et al."
        return Citation(
            pmid=record.pmid,
            title=record.title,
            authors_display=authors_display,
            pub_year=record.pub_year,
        )

    # ──────────────────────────────────────────────────────────────────────────
    # LLM search plan generation
    # ──────────────────────────────────────────────────────────────────────────

    def _generate_search_plan(
        self, protocol_text: str, params: ProtocolParameters
    ) -> SearchPlan:
        fallback = SearchPlan(
            endpoint_hypothesis=None,
            endpoint_search_query=self._fallback_endpoint_query(params),
            alternatives=[],
        )

        # Step 1: extract scientific_question, endpoint_description, current_method
        summary = self._summarize_study(protocol_text)
        if summary:
            logger.info(
                "Study summary — question: %s | endpoint: %s | method: %s",
                summary.scientific_question[:80],
                summary.endpoint_description[:80],
                summary.current_method[:80],
            )
            # endpoint_description drives Path A; use it as the endpoint_search_query
            fallback = SearchPlan(
                endpoint_hypothesis=summary.scientific_question,
                endpoint_search_query=summary.endpoint_description,
                alternatives=[],
            )

        # Step 2: generate Path B alternative method descriptions
        # Pass the current_method summary so the LLM knows exactly what to replace
        enriched_text = (
            f"{protocol_text.strip()}\n\n"
            f"[CURRENT METHOD SUMMARY]: {summary.current_method}"
            if summary else protocol_text
        )
        prompt = build_alternative_query_prompt(
            protocol_text=enriched_text,
            endpoint_category=params.endpoint_category,
            study_domain=params.study_domain,
            species=params.species,
            route=params.route,
            procedure_text=params.procedure_text,
        )
        raw = self._llm.call(prompt, max_tokens=_PLAN_MAX_TOKENS, json_mode=True)
        if raw is None:
            logger.warning("Search plan LLM unavailable — using keyword fallback")
            return fallback
        try:
            payload = json.loads(raw)
        except (json.JSONDecodeError, AttributeError) as exc:
            logger.warning("Search plan parse error: %s", exc)
            return fallback

        alternatives = [
            LLMProposedAlternative(
                three_r_class=alt.get("three_r_class", "refinement"),
                method_description=alt.get("method_description", ""),
            )
            for alt in payload.get("alternatives", [])
            if alt.get("method_description")
        ]
        # Enforce Replace > Reduce > Refine order so Path B searches are dispatched
        # in priority order (asyncio.gather preserves task order in results).
        _ORDER = {"replacement": 0, "reduction": 1, "refinement": 2}
        alternatives.sort(key=lambda a: _ORDER.get(a.three_r_class, 3))

        return SearchPlan(
            endpoint_hypothesis=(
                summary.scientific_question if summary
                else payload.get("endpoint_hypothesis")
            ),
            endpoint_search_query=(
                summary.endpoint_description if summary
                else payload.get("endpoint_search_query", self._fallback_endpoint_query(params))
            ),
            alternatives=alternatives,
        )

    def _summarize_study(self, study_text: str) -> StudySummary | None:
        """Extract scientific_question, endpoint_description, current_method from free text."""
        prompt = build_study_summary_prompt(study_text)
        raw = self._llm.call(prompt, max_tokens=512, json_mode=True)
        if raw is None:
            return None
        try:
            payload = json.loads(raw)
        except (json.JSONDecodeError, AttributeError) as exc:
            logger.warning("Study summary parse error: %s", exc)
            return None
        q = payload.get("scientific_question", "").strip()
        e = payload.get("endpoint_description", "").strip()
        m = payload.get("current_method", "").strip()
        if not (q and e and m):
            return None
        return StudySummary(
            scientific_question=q,
            endpoint_description=e,
            current_method=m,
        )

    @staticmethod
    def _fallback_endpoint_query(params: ProtocolParameters) -> str:
        parts = []
        if params.endpoint_category:
            parts.append(params.endpoint_category.replace("_", " "))
        if params.procedure_text:
            parts.append(params.procedure_text)
        if params.study_domain and params.study_domain != "general":
            parts.append(params.study_domain.replace("_", " "))
        return " ".join(parts) if parts else "toxicology endpoint assessment"
