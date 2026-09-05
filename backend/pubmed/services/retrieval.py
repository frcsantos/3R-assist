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
import re
from collections import defaultdict
from dataclasses import dataclass, field

from app.adapters.embedder import EmbedderAdapter
from app.adapters.llm import LLMAdapter
from app.models.protocol import ProtocolParameters
from pubmed.db.repository import PubMedRepository
from pubmed.models.analysis import Citation, LLMProposedAlternative, PubMedRecommendation, SupportingPaper
from pubmed.models.record import Author, PubMedRecord
from pubmed.prompts.alternative_query import build_alternative_query_prompt
from pubmed.prompts.ranking import build_ranking_prompt
from pubmed.prompts.study_summary import build_study_summary_prompt
from pubmed.prompts.summary import build_summary_prompt
from pubmed.skills import classify_domain

logger = logging.getLogger(__name__)

# How many vector-search candidates each query retrieves.
# Replacement gets the most — biases the candidate pool before scoring.
TOP_K_ENDPOINT = 15
TOP_K_BY_CLASS: dict[str, int] = {
    "replacement": 20,
    "reduction":   15,
    "refinement":   8,
}

# Final score = cosine × weight. Replace stays at 1.0 so a strong replacement
# always beats an equal-cosine reduction or refinement.
THREE_R_WEIGHTS: dict[str, float] = {
    "replacement": 1.00,
    "reduction":   0.65,
    "refinement":  0.35,
}

_PLAN_MAX_TOKENS = 512
_RANK_MAX_TOKENS = 6000
_SUMMARY_MAX_TOKENS = 512
_CANDIDATES_FOR_LLM = 15       # used by cosine fallback
_MAX_PATH_A_FOR_LLM = 5        # Path A candidates sent to ranker
_ABSTRACT_CHAR_LIMIT = 1000  # truncate abstracts sent to LLM — enough to reach Methods section
_MIN_COSINE_FALLBACK = 0.5  # if LLM includes nothing, return candidates above this score


# Words stripped before building the grouping key so that minor label variants
# ("HepaRG model" vs "HepaRG assay") map to the same canonical key.
_GROUP_STOP = frozenset({
    "a", "an", "the", "for", "of", "in", "on", "to", "and", "or",
    "with", "as", "by", "using", "via", "based", "derived",
    "model", "assay", "method", "test", "approach",
})


def _normalize_group_key(label: str) -> str:
    """Return a canonical, order-independent key for grouping method labels."""
    words = re.sub(r"[^\w\s]", "", label.lower()).split()
    significant = [w for w in words if w not in _GROUP_STOP] or words
    return " ".join(sorted(significant))


@dataclass
class _Candidate:
    record: PubMedRecord
    cosine: float
    source_class: str | None = None   # three_r_class from whichever path found it first
    source_query: str | None = None   # Path B only: the specific alternative method text


@dataclass
class StudySummary:
    scientific_question: str
    endpoint_descriptions: list[str]
    current_method: str


@dataclass
class SearchPlan:
    endpoint_hypothesis: str
    endpoint_search_queries: list[str]
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
        """
        plan, rank_guidance = await self._generate_search_plan(protocol_text, params)

        logger.info(
            "Search plan — endpoint_queries: %d, alternatives: %d, hypothesis: %s",
            len(plan.endpoint_search_queries),
            len(plan.alternatives),
            (plan.endpoint_hypothesis or "")[:120],
        )
        for i, q in enumerate(plan.endpoint_search_queries):
            logger.info("  Path A[%d]: %s", i, q[:100])
        for a in plan.alternatives:
            logger.info("  Path B [%s]: %s", a.three_r_class, a.method_description[:80])

        path_a_tasks = [
            asyncio.create_task(self._path_a_endpoint(q))
            for q in plan.endpoint_search_queries
        ]
        path_b_task = asyncio.create_task(
            self._path_b_reconstruction(plan.alternatives)
        )

        gathered = await asyncio.gather(*path_a_tasks + [path_b_task])
        path_b_results = gathered[-1]
        path_a_batches = gathered[:-1]
        path_a_results = [c for batch in path_a_batches for c in batch]

        logger.info(
            "Candidates — Path A: %d, Path B: %d",
            len(path_a_results), len(path_b_results),
        )

        # Merge: keep the highest cosine per PMID.
        merged: dict[str, _Candidate] = {}
        for candidate in path_a_results + path_b_results:
            existing = merged.get(candidate.record.pmid)
            if existing is None or candidate.cosine > existing.cosine:
                merged[candidate.record.pmid] = candidate

        total_candidates = len(merged)
        logger.info("Merged unique candidates: %d → sending to ranker", total_candidates)
        if not merged:
            return [], plan.endpoint_hypothesis, 0

        sorted_candidates = sorted(merged.values(), key=lambda c: -c.cosine)

        # Split candidates into Path A (no source_query) and Path B (specific alternative).
        path_a = [c for c in sorted_candidates if not c.source_query]
        path_b = [c for c in sorted_candidates if c.source_query]

        # Pre-group Path B by the specific alternative query that retrieved each paper.
        # Send only the top-scoring representative per group to the ranker — siblings are
        # auto-promoted as supporting papers if their rep is included.
        path_b_by_query: dict[str, list[_Candidate]] = defaultdict(list)
        for c in path_b:
            path_b_by_query[c.source_query].append(c)

        path_b_reps: list[_Candidate] = []
        path_b_siblings: dict[str, list[_Candidate]] = {}  # rep pmid → sibling candidates
        for group in path_b_by_query.values():
            group.sort(key=lambda c: -c.cosine)
            rep = group[0]
            path_b_reps.append(rep)
            if len(group) > 1:
                path_b_siblings[rep.record.pmid] = group[1:]

        llm_candidates = path_a[:_MAX_PATH_A_FOR_LLM] + path_b_reps
        llm_input = [
            {
                "pmid": c.record.pmid,
                "title": c.record.title,
                "abstract_text": (c.record.abstract_text or "")[:_ABSTRACT_CHAR_LIMIT],
                "source_class": c.source_class,
            }
            for c in llm_candidates
        ]

        logger.info(
            "LLM input — path_a: %d, path_b reps: %d (siblings held: %d)",
            len(path_a[:_MAX_PATH_A_FOR_LLM]), len(path_b_reps),
            sum(len(v) for v in path_b_siblings.values()),
        )

        record_by_pmid = {c.record.pmid: c.record for c in sorted_candidates}
        cosine_by_pmid = {c.record.pmid: c.cosine for c in sorted_candidates}
        path_by_pmid = {
            c.record.pmid: ("alternative_search" if c.source_class else "endpoint_search")
            for c in sorted_candidates
        }
        ranked_meta = await self._rank_with_llm(params, llm_input, endpoint_hypothesis=plan.endpoint_hypothesis, rank_guidance=rank_guidance)
        if ranked_meta:
            # Inject siblings of included Path B reps — they share the same method group.
            already_included = {r["pmid"] for r in ranked_meta if r.get("include")}
            extra: list[dict] = []
            for entry in ranked_meta:
                if not entry.get("include"):
                    continue
                siblings = path_b_siblings.get(entry.get("pmid", ""), [])
                if not siblings:
                    continue
                # If the primary has no method_group, assign a synthetic key so it
                # and all its siblings share the same group in _build_recommendations.
                if not entry.get("method_group"):
                    entry["method_group"] = f"_group_{entry['pmid']}"
                for sibling in siblings:
                    if sibling.record.pmid not in already_included:
                        extra.append({
                            "pmid": sibling.record.pmid,
                            "include": True,
                            "three_r_class": entry.get("three_r_class"),
                            "method_group": entry.get("method_group"),
                            "relevance_explanation": "Supporting paper from the same method group.",
                            "endpoint_category": entry.get("endpoint_category"),
                        })
                        already_included.add(sibling.record.pmid)
            if extra:
                ranked_meta = ranked_meta + extra

            included = [r for r in ranked_meta if r.get("include")]
            excluded = [r for r in ranked_meta if not r.get("include")]
            logger.info("Ranker: %d included (%d siblings), %d excluded", len(included), len(extra), len(excluded))
            for r in included:
                logger.info("  INCLUDE [%s] %s | group: %s", r.get("three_r_class"), r.get("pmid"), r.get("method_group"))
            for r in excluded[:5]:
                logger.info("  EXCLUDE %s — %s", r.get("pmid"), r.get("relevance_explanation", "")[:60])
            recommendations = self._build_recommendations(
                ranked_meta, record_by_pmid, cosine_by_pmid, path_by_pmid
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
            _Candidate(record=rec, cosine=score, source_class=alt.three_r_class, source_query=alt.method_description)
            for rec, score in rows
        ]

    # ──────────────────────────────────────────────────────────────────────────
    # LLM-based ranking and filtering
    # ──────────────────────────────────────────────────────────────────────────

    async def _rank_with_llm(
        self,
        params: ProtocolParameters,
        candidates: list[dict],
        endpoint_hypothesis: str | None = None,
        rank_guidance: str = "",
    ) -> list[dict] | None:
        prompt = build_ranking_prompt(
            endpoint_category=params.endpoint_category,
            study_domain=params.study_domain,
            procedure_text=params.procedure_text,
            endpoint_hypothesis=endpoint_hypothesis,
            candidates=candidates,
            rank_guidance=rank_guidance,
        )
        raw = await self._llm.async_call(prompt, max_tokens=_RANK_MAX_TOKENS, json_mode=True)
        try:
            with open("/tmp/rank_debug.json", "w") as _f:
                import json as _json
                _json.dump({"prompt": prompt, "response": raw}, _f, indent=2)
        except Exception:
            pass
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
        path_by_pmid: dict[str, str],
    ) -> list[PubMedRecommendation]:
        scored: list[tuple[PubMedRecord, float, dict]] = []
        for item in ranked_meta:
            if not item.get("include", False):
                continue
            pmid = item.get("pmid", "")
            record = record_by_pmid.get(pmid)
            if record is None:
                continue
            three_r = item.get("three_r_class") or "refinement"
            if three_r not in THREE_R_WEIGHTS:
                three_r = "refinement"
            cosine = cosine_by_pmid.get(pmid, 0.0)
            weighted = round(cosine * THREE_R_WEIGHTS[three_r], 4)
            scored.append((record, weighted, item))

        scored.sort(key=lambda x: -x[1])

        # Group by method_group label. Papers without a label each stand alone.
        # Normalize the key so minor wording differences ("HepaRG model" vs
        # "HepaRG assay") still group together.
        groups: dict[str, list[tuple[PubMedRecord, float, dict]]] = defaultdict(list)
        for entry in scored:
            record, _, meta = entry
            label = (meta.get("method_group") or "").strip()
            key = _normalize_group_key(label) if label else f"__solo_{record.pmid}"
            groups[key].append(entry)

        # Best-scored paper in each group is primary; others become supporting_papers.
        primaries: list[tuple[PubMedRecord, float, dict, list[SupportingPaper]]] = []
        for entries in groups.values():
            primary_record, primary_weighted, primary_meta = entries[0]
            supporting = [
                SupportingPaper(
                    pmid=rec.pmid,
                    doi=rec.doi,
                    title=rec.title,
                    pub_year=rec.pub_year,
                )
                for rec, _, _ in entries[1:]
            ]
            primaries.append((primary_record, primary_weighted, primary_meta, supporting))

        primaries.sort(key=lambda x: -x[1])

        return [
            PubMedRecommendation(
                record=record,
                relevance_score=weighted,
                relevance_explanation=meta.get("relevance_explanation") or "",
                three_r_class=meta.get("three_r_class") or "refinement",
                endpoint_category=meta.get("endpoint_category") or None,
                rank=rank,
                search_path=path_by_pmid.get(record.pmid, "endpoint_search"),
                method_group=(meta.get("method_group") or "").strip() or None,
                supporting_papers=supporting,
            )
            for rank, (record, weighted, meta, supporting) in enumerate(primaries, start=1)
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
                    search_path="alternative_search" if c.source_class else "endpoint_search",
                )
            )
        return results

    # ──────────────────────────────────────────────────────────────────────────
    # Post-ranking synthesis: summary + citations
    # ──────────────────────────────────────────────────────────────────────────

    async def generate_summary(
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

        raw = await self._llm.async_call(prompt, max_tokens=_SUMMARY_MAX_TOKENS, json_mode=True)
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

    async def _generate_search_plan(
        self, protocol_text: str, params: ProtocolParameters
    ) -> tuple[SearchPlan, str]:
        """Returns (plan, rank_guidance) — rank_guidance is passed to the ranker."""
        profile = classify_domain(protocol_text, params.endpoint_category)
        logger.info("Domain profile: %s", profile.name)

        fallback_query = self._fallback_endpoint_query(params)
        fallback = SearchPlan(
            endpoint_hypothesis=None,
            endpoint_search_queries=[fallback_query],
            alternatives=[],
        )

        # Step 1: extract scientific_question, endpoint_descriptions, current_method
        summary = await self._summarize_study(protocol_text)
        if summary:
            logger.info(
                "Study summary — question: %s | endpoints: %d | method: %s",
                summary.scientific_question[:80],
                len(summary.endpoint_descriptions),
                summary.current_method[:80],
            )
            fallback = SearchPlan(
                endpoint_hypothesis=summary.scientific_question,
                endpoint_search_queries=summary.endpoint_descriptions,
                alternatives=[],
            )

        # Step 2: generate Path B alternative method descriptions using profile vocabulary
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
            vocabulary=profile.vocabulary,
        )
        raw = await self._llm.async_call(prompt, max_tokens=_PLAN_MAX_TOKENS, json_mode=True)
        if raw is None:
            logger.warning("Search plan LLM unavailable — using keyword fallback")
            return fallback, profile.rank_guidance
        try:
            payload = json.loads(raw)
        except (json.JSONDecodeError, AttributeError) as exc:
            logger.warning("Search plan parse error: %s", exc)
            return fallback, profile.rank_guidance

        alternatives = [
            LLMProposedAlternative(
                three_r_class=alt.get("three_r_class") or "refinement",
                method_description=alt.get("method_description", ""),
            )
            for alt in payload.get("alternatives", [])
            if alt.get("method_description")
        ]

        # Step 3: add profile-defined injections
        # Always-on injections come first (highest priority)
        for inj in profile.base_path_b:
            alternatives.insert(0, inj)
            logger.info("Profile Path B injection [%s]: %s", inj.three_r_class, inj.method_description[:60])

        # Subacute / organ-toxicity extension — only when the profile defines signals
        # and the protocol text contains them
        has_subacute = profile.has_subacute(protocol_text)
        if has_subacute:
            for inj in profile.subacute_path_b:
                alternatives.insert(0, inj)
                logger.info("Subacute Path B injection [%s]: %s", inj.three_r_class, inj.method_description[:60])

        # Enforce Replace > Reduce > Refine order
        _ORDER = {"replacement": 0, "reduction": 1, "refinement": 2}
        alternatives.sort(key=lambda a: _ORDER.get(a.three_r_class, 3))

        # Endpoint queries: LLM-generated + profile injections
        endpoint_queries = list(
            summary.endpoint_descriptions if summary
            else [payload.get("endpoint_search_query") or self._fallback_endpoint_query(params)]
        )
        endpoint_queries.extend(profile.base_path_a)
        if has_subacute:
            endpoint_queries.extend(profile.subacute_path_a)
            logger.info("Subacute Path A endpoint queries injected")

        return SearchPlan(
            endpoint_hypothesis=(
                summary.scientific_question if summary
                else payload.get("endpoint_hypothesis")
            ),
            endpoint_search_queries=endpoint_queries,
            alternatives=alternatives,
        ), profile.rank_guidance

    async def _summarize_study(self, study_text: str) -> StudySummary | None:
        """Extract scientific_question, endpoint_descriptions, current_method from free text."""
        prompt = build_study_summary_prompt(study_text)
        raw = await self._llm.async_call(prompt, max_tokens=600, json_mode=True)
        if raw is None:
            return None
        try:
            payload = json.loads(raw)
        except (json.JSONDecodeError, AttributeError) as exc:
            logger.warning("Study summary parse error: %s", exc)
            return None
        q = payload.get("scientific_question", "").strip()
        m = payload.get("current_method", "").strip()
        # Accept list or legacy single string for endpoint_descriptions
        raw_endpoints = payload.get("endpoint_descriptions") or payload.get("endpoint_description")
        if isinstance(raw_endpoints, str):
            endpoints = [raw_endpoints.strip()] if raw_endpoints.strip() else []
        elif isinstance(raw_endpoints, list):
            endpoints = [e.strip() for e in raw_endpoints if isinstance(e, str) and e.strip()]
        else:
            endpoints = []
        if not (q and endpoints and m):
            return None
        return StudySummary(
            scientific_question=q,
            endpoint_descriptions=endpoints,
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
