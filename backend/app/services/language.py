"""Detect Portuguese vs English from source text for matching and extraction."""

from __future__ import annotations

import re
from typing import Literal

LangCode = Literal["pt", "en"]

_TOKEN_RE = re.compile(r"[a-záàâãéêíóôõúüç]+", re.IGNORECASE)
_PT_CHARS_RE = re.compile(r"[ãõçáàâéêíóôúüÃÕÇÁÀÂÉÊÍÓÔÚÜ]")

# Distinctive function words; shared scientific terms are ignored.
_PT_MARKERS = frozenset(
    {
        "que",
        "para",
        "uma",
        "uns",
        "nao",
        "não",
        "dos",
        "das",
        "pelo",
        "pela",
        "pelos",
        "pelas",
        "este",
        "esta",
        "estes",
        "estas",
        "isso",
        "isto",
        "também",
        "tambem",
        "sobre",
        "mais",
        "como",
        "mas",
        "sao",
        "são",
        "está",
        "foram",
        "sera",
        "será",
        "nesta",
        "neste",
        "dessa",
        "desse",
        "entre",
        "quando",
        "onde",
        "sem",
        "apos",
        "após",
        "ate",
        "até",
        "muito",
        "pode",
        "devem",
        "deve",
        "conforme",
        "resolucao",
        "resolução",
        "normativa",
        "anexo",
        "artigo",
        "portaria",
        "estudo",
        "ensaios",
        "ensaio",
        "animais",
        "protocolo",
        "método",
        "metodo",
        "métodos",
        "via",
    }
)
_EN_MARKERS = frozenset(
    {
        "the",
        "and",
        "with",
        "from",
        "this",
        "that",
        "which",
        "were",
        "was",
        "are",
        "been",
        "have",
        "has",
        "their",
        "these",
        "those",
        "into",
        "than",
        "such",
        "using",
        "used",
        "under",
        "after",
        "before",
        "during",
        "each",
        "study",
        "studies",
        "guideline",
        "guidelines",
        "testing",
        "animals",
        "protocol",
        "method",
        "methods",
    }
)


def detect_lang(text: str | None) -> LangCode:
    """Return ``pt`` or ``en`` from running text. Defaults to English."""
    sample = (text or "").strip()
    if not sample:
        return "en"

    tokens = _TOKEN_RE.findall(sample.casefold())
    pt_score = sum(1 for token in tokens if token in _PT_MARKERS)
    en_score = sum(1 for token in tokens if token in _EN_MARKERS)
    pt_score += 2 * len(_PT_CHARS_RE.findall(sample))

    if pt_score > en_score:
        return "pt"
    return "en"


def language_label(lang: LangCode) -> str:
    return "Portuguese" if lang == "pt" else "English"
