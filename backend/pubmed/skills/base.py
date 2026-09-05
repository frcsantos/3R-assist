from __future__ import annotations

from dataclasses import dataclass, field

from pubmed.models.analysis import LLMProposedAlternative


@dataclass
class DomainProfile:
    name: str

    # Vocabulary block injected into the alternative-query prompt
    vocabulary: str

    # Always-on Path B (method-embedding) injections for this domain
    base_path_b: list[LLMProposedAlternative] = field(default_factory=list)

    # Always-on Path A (endpoint-embedding) injections for this domain
    base_path_a: list[str] = field(default_factory=list)

    # Guidance appended to the ranker's include/exclude section
    rank_guidance: str = ""

    # ── Subacute / organ-toxicity extension ──────────────────────────────────
    # Activated only when these signals appear in the protocol text.
    # Keeps organ-model injection scoped to protocols that actually need it.
    subacute_signals: tuple[str, ...] = field(default_factory=tuple)
    subacute_path_b: list[LLMProposedAlternative] = field(default_factory=list)
    subacute_path_a: list[str] = field(default_factory=list)

    def has_subacute(self, protocol_text: str) -> bool:
        lowered = protocol_text.lower()
        return any(sig in lowered for sig in self.subacute_signals)
