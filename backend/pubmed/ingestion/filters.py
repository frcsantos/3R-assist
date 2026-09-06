"""
Term clusters used to filter PubMed records at ingestion time.

A record passes if it matches ANY of the clusters. Within each cluster,
at least one term must appear in the lowercased title + abstract + MeSH terms.

`match_cluster()` returns the name of the first matching cluster, or None.
`passes_filter()` is a convenience bool wrapper kept for compatibility.
"""

from __future__ import annotations

# ── Cluster 1: Core 3Rs / alternative methods ───────────────────────────────
CLUSTER_3RS = frozenset(
    {
        "3rs",
        "three rs",
        "replace reduce refine",
        "replacement method",
        "alternative method",
        "non-animal",
        "animal-free",
        "animal testing alternative",
        "animal use alternative",
        "humane endpoint",
        "nam",
        "new approach method",
        "new approach methods",
        "substitution method",
        "substitutive method",
    }
)

# ── Cluster 2: In vitro / organotypic systems ────────────────────────────────
CLUSTER_IN_VITRO = frozenset(
    {
        "organoid",
        "organ-on-a-chip",
        "microphysiological",
        "reconstructed human epidermis",
        "reconstructed human corneal",
        "epiderm",
        "episkin",
        "skinethic",
        "epiocu",
        "3d cell culture",
        "3d skin model",
        "spheroid",
        "air-liquid interface",
        "stem cell model",
        "ipsc-derived",
        "induced pluripotent",
    }
)

# ── Cluster 3: Computational / in silico ─────────────────────────────────────
CLUSTER_IN_SILICO = frozenset(
    {
        "in silico",
        "computational toxicology",
        "qsar",
        "quantitative structure-activity",
        "read-across",
        "adverse outcome pathway",
        "physiologically based pharmacokinetic",
        "pbpk",
        "machine learning toxicity",
        "deep learning toxicity",
        "toxicokinetic model",
    }
)

# ── Cluster 4: Endpoint-specific validated alternative tests ─────────────────
CLUSTER_VALIDATED_TESTS = frozenset(
    {
        # Skin irritation / corrosion
        "epiderm",
        "episkin",
        "skinethic rhe",
        "transcutaneous electrical resistance",
        "oecd 431",
        "oecd 439",
        # Eye irritation
        "bovine corneal opacity",
        "bcop",
        "isolated chicken eye",
        "het-cam",
        "hen's egg chorioallantoic",
        "epiocu",
        "rhce",
        "vitrigel-eye",
        "eveit",
        # Skin sensitisation
        "dpra",
        "direct peptide reactivity",
        "keratinosens",
        "lusens",
        "h-clat",
        "human cell line activation",
        "are-nrf2",
        "genomic allergen rapid detection",
        "gard assay",
        "u-sens",
        "oecd 442",
        # Genotoxicity
        "ames test",
        "bacterial reverse mutation",
        "in vitro micronucleus",
        "in vitro chromosomal aberration",
        "comet assay",
        "toxtracker",
        "γh2ax",
        "gh2ax",
        # Phototoxicity
        "3t3 nru",
        "neutral red uptake phototoxicity",
        "oecd 432",
        # Pyrogenicity
        "monocyte activation test",
        " mat ",
        "recombinant factor c",
        "rfc assay",
        "human whole blood test",
        # Acute toxicity
        "zebrafish embryo",
        "fish embryo toxicity",
        "fet test",
        "oecd 236",
        "ld50 alternative",
        "fixed dose procedure",
        "up-and-down procedure",
        # Skin absorption
        "franz cell",
        "diffusion cell",
        "pampa",
        "parallel artificial membrane",
        "caco-2 permeability",
    }
)

# ── Cluster 5: Botulinum toxin potency alternatives ──────────────────────────
CLUSTER_BOTULINUM = frozenset(
    {
        "botulinum toxin potency",
        "botulinum neurotoxin potency",
        "botulinum toxin alternative",
        "cell-based potency assay",
        "cell based potency assay",
        "snap-25 cleavage",
        "snap25 cleavage",
        "endopeptidase assay botulinum",
        "mouse bioassay botulinum",
        "mouse lethality assay botulinum",
        "neuro-2a botulinum",
        "neuro2a botulinum",
        "ipsc neuron botulinum",
        "phrenic nerve hemidiaphragm",
        "elisa botulinum potency",
        "mouse bioassay replacement",
    }
)

_CLUSTER_MAP: list[tuple[str, frozenset[str]]] = [
    ("3rs", CLUSTER_3RS),
    ("in_vitro", CLUSTER_IN_VITRO),
    ("in_silico", CLUSTER_IN_SILICO),
    ("validated_tests", CLUSTER_VALIDATED_TESTS),
    ("botulinum", CLUSTER_BOTULINUM),
]


def match_cluster(title: str, abstract: str, mesh_terms: list[str]) -> str | None:
    """Return the name of the first matching cluster, or None if no match."""
    haystack = " ".join([title, abstract, " ".join(mesh_terms)]).lower()
    for name, cluster in _CLUSTER_MAP:
        if any(term in haystack for term in cluster):
            return name
    return None


def passes_filter(title: str, abstract: str, mesh_terms: list[str]) -> bool:
    return match_cluster(title, abstract, mesh_terms) is not None
