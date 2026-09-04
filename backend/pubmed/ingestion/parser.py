"""Parse PubMed XML baseline files (gzipped or plain).

Structured abstracts (labelled sections) are split into two text fields:
  endpoint_text — Background, Objective, Aims, Conclusions
  method_text   — Methods, Results, Findings

Unstructured abstracts (single block) fall back to using the full text for both,
so both embedding columns remain searchable even for older records.
"""

from __future__ import annotations

import gzip
import re
import xml.etree.ElementTree as ET
from pathlib import Path
from typing import Iterator

from pubmed.ingestion.filters import match_cluster
from pubmed.models.record import Author, PubMedRecord

_MONTH_MAP: dict[str, int] = {
    "jan": 1, "feb": 2, "mar": 3, "apr": 4, "may": 5, "jun": 6,
    "jul": 7, "aug": 8, "sep": 9, "oct": 10, "nov": 11, "dec": 12,
}

# Abstract section labels that describe WHAT was studied (endpoint/hypothesis context)
_ENDPOINT_LABELS = frozenset({
    "background", "introduction", "objective", "objectives",
    "aim", "aims", "purpose", "rationale",
    "conclusion", "conclusions", "summary",
})

# Abstract section labels that describe HOW it was done (methodological context)
_METHOD_LABELS = frozenset({
    "methods", "method", "materials and methods", "material and methods",
    "experimental design", "study design", "procedures", "experimental procedures",
    "results", "findings", "observations",
})


def _text(element: ET.Element | None, tag: str) -> str | None:
    if element is None:
        return None
    child = element.find(tag)
    return child.text.strip() if child is not None and child.text else None


def _parse_pub_date(article: ET.Element) -> tuple[int | None, int | None]:
    pub_date = article.find(".//PubDate")
    if pub_date is None:
        return None, None
    year_el = pub_date.find("Year")
    year = int(year_el.text) if year_el is not None and year_el.text else None
    month_el = pub_date.find("Month")
    month = None
    if month_el is not None and month_el.text:
        raw = month_el.text.strip().lower()[:3]
        month = _MONTH_MAP.get(raw) or (int(raw) if raw.isdigit() else None)
    return year, month


def _parse_abstract(
    article: ET.Element,
) -> tuple[str, str, str] | None:
    """Return (full_text, endpoint_text, method_text) or None if no abstract."""
    abstract_el = article.find("Abstract")
    if abstract_el is None:
        return None

    endpoint_parts: list[str] = []
    method_parts: list[str] = []
    all_parts: list[str] = []

    elements = abstract_el.findall("AbstractText")
    for elem in elements:
        label = (elem.get("Label") or "").strip().lower()
        text = "".join(elem.itertext()).strip()
        if not text:
            continue

        labelled = f"{elem.get('Label')}: {text}" if elem.get("Label") else text
        all_parts.append(labelled)

        if label in _ENDPOINT_LABELS:
            endpoint_parts.append(text)
        elif label in _METHOD_LABELS:
            method_parts.append(text)
        else:
            # Unlabelled or unknown label: include in both to avoid gaps
            endpoint_parts.append(text)
            method_parts.append(text)

    full_text = " ".join(all_parts)
    if not full_text:
        return None

    # Structured abstract: use labelled sections
    if len(elements) > 1 and any(e.get("Label") for e in elements):
        endpoint_text = " ".join(endpoint_parts) if endpoint_parts else full_text
        method_text = " ".join(method_parts) if method_parts else full_text
    else:
        # Unstructured: use full text for both paths
        endpoint_text = full_text
        method_text = full_text

    return full_text, endpoint_text, method_text


def _parse_authors(article: ET.Element) -> tuple[list[Author], list[str]]:
    authors: list[Author] = []
    institutions: set[str] = set()
    author_list = article.find("AuthorList")
    if author_list is None:
        return authors, []
    for author_el in author_list.findall("Author"):
        last = _text(author_el, "LastName")
        fore = _text(author_el, "ForeName") or _text(author_el, "Initials")
        affil_el = author_el.find("AffiliationInfo/Affiliation")
        affil = affil_el.text.strip() if affil_el is not None and affil_el.text else None
        if affil:
            institution = re.split(r",|\.", affil)[0].strip()
            if institution:
                institutions.add(institution)
        authors.append(Author(last_name=last, fore_name=fore, affiliation=affil))
    return authors, sorted(institutions)


def _parse_mesh_terms(citation: ET.Element) -> list[str]:
    terms: list[str] = []
    for heading in citation.findall("MeshHeadingList/MeshHeading"):
        descriptor = heading.find("DescriptorName")
        if descriptor is not None and descriptor.text:
            terms.append(descriptor.text.strip())
    return terms


def _parse_journal(article: ET.Element) -> str | None:
    journal_el = article.find("Journal")
    if journal_el is None:
        return None
    title_el = journal_el.find("Title")
    if title_el is not None and title_el.text:
        return title_el.text.strip()
    iso_el = journal_el.find("ISOAbbreviation")
    return iso_el.text.strip() if iso_el is not None and iso_el.text else None


def _parse_article(citation: ET.Element) -> PubMedRecord | None:
    pmid_el = citation.find("PMID")
    if pmid_el is None or not pmid_el.text:
        return None

    article = citation.find("Article")
    if article is None:
        return None

    title_el = article.find("ArticleTitle")
    title = "".join(title_el.itertext()).strip() if title_el is not None else ""
    if not title:
        return None

    abstract_result = _parse_abstract(article)
    if abstract_result is None:
        return None
    abstract_text, endpoint_text, method_text = abstract_result

    mesh_terms = _parse_mesh_terms(citation)

    cluster = match_cluster(title, abstract_text, mesh_terms)
    if cluster is None:
        return None

    pub_year, pub_month = _parse_pub_date(article)
    authors, institutions = _parse_authors(article)
    journal = _parse_journal(article)

    return PubMedRecord(
        pmid=pmid_el.text.strip(),
        title=title,
        authors=authors,
        institutions=institutions,
        pub_year=pub_year,
        pub_month=pub_month,
        journal=journal,
        abstract_text=abstract_text,
        endpoint_text=endpoint_text,
        method_text=method_text,
        mesh_terms=mesh_terms,
        cluster=cluster,
    )


def parse_file(path: Path) -> Iterator[PubMedRecord]:
    """Yield filtered PubMedRecord objects from a .xml or .xml.gz file."""
    open_fn = gzip.open if path.suffix == ".gz" else open
    with open_fn(path, "rb") as fh:
        for _event, element in ET.iterparse(fh, events=("end",)):
            if element.tag != "MedlineCitation":
                continue
            record = _parse_article(element)
            if record is not None:
                yield record
            element.clear()
