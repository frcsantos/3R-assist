"""MethodRepository — query logic for curated methods."""

from __future__ import annotations

import json
from collections import defaultdict

from app.db.connection import get_pool
from app.models.i18n import parse_localized_str, parse_localized_str_list
from app.models.method import Method, MethodRegulatoryContext


class MethodRepository:
    _SELECT_COLUMNS = """
        m.id, m.slug, m.active, m.name, m.description,
        m.endpoint_category, m.routes_applicable, m.study_domain,
        m.oecd_ref, m.ncit_id,
        COALESCE(NULLIF(BTRIM(m.source_citation), ''), sd.doc_ref) AS source_citation,
        m.source_doc_id,
        sd.url AS source_url,
        m.source_db,
        m.replacement_rationale, m.reduction_rationale, m.refinement_rationale,
        m.keywords, m.text_for_embedding, m.embedding_json,
        m.created_at, m.updated_at
    """

    _FROM_METHODS = """
        FROM methods m
        LEFT JOIN documents sd ON sd.id = m.source_doc_id
    """

    _SELECT_ACTIVE = f"""
        SELECT {_SELECT_COLUMNS}
        {_FROM_METHODS}
        WHERE m.active = TRUE
        ORDER BY m.slug
    """

    _SELECT_CONTEXTS = """
        SELECT
            mrc.method_id, mrc.jurisdiction, mrc.validation_status,
            mrc.regulation_status, mrc.regulation_date, mrc.regulation_purpose,
            mrc.regulatory_body, mrc.regulatory_doc_id,
            COALESCE(
                NULLIF(BTRIM(mrc.regulatory_citation), ''),
                rd.doc_ref
            ) AS regulatory_citation,
            rd.url AS regulatory_url,
            mrc.notes
        FROM method_regulatory_contexts mrc
        LEFT JOIN documents rd ON rd.id = mrc.regulatory_doc_id
        WHERE mrc.method_id = ANY($1::int[])
        ORDER BY mrc.method_id, mrc.jurisdiction
    """

    async def list_active(self) -> list[Method]:
        methods, _ = await self.list_active_with_contexts()
        return methods

    async def list_active_with_contexts(
        self,
    ) -> tuple[list[Method], dict[int, list[MethodRegulatoryContext]]]:
        pool = await get_pool()
        async with pool.acquire() as conn:
            rows = await conn.fetch(self._SELECT_ACTIVE)
            if not rows:
                return [], {}

            methods = [self._row_to_method(row) for row in rows]
            method_ids = [method.id for method in methods]
            context_rows = await conn.fetch(self._SELECT_CONTEXTS, method_ids)

        contexts_by_method: dict[int, list[MethodRegulatoryContext]] = defaultdict(list)
        for row in context_rows:
            contexts_by_method[row["method_id"]].append(self._row_to_context(row))

        return methods, dict(contexts_by_method)

    async def find_by_oecd_ref(
        self,
        oecd_ref: str,
        *,
        include_inactive: bool = True,
    ) -> list[Method]:
        normalized = " ".join(oecd_ref.split()).strip()
        if not normalized:
            return []

        pool = await get_pool()
        async with pool.acquire() as conn:
            rows = await conn.fetch(
                f"""
                SELECT {self._SELECT_COLUMNS}
                {self._FROM_METHODS}
                WHERE m.oecd_ref IS NOT NULL
                  AND lower(regexp_replace(trim(m.oecd_ref), '\\s+', ' ', 'g'))
                      = lower($1)
                  AND ($2::boolean OR m.active = TRUE)
                ORDER BY m.slug
                """,
                normalized,
                include_inactive,
            )
        return [self._row_to_method(row) for row in rows]

    async def list_for_text_match(
        self,
        *,
        include_inactive: bool = True,
    ) -> list[Method]:
        pool = await get_pool()
        async with pool.acquire() as conn:
            rows = await conn.fetch(
                f"""
                SELECT {self._SELECT_COLUMNS}
                {self._FROM_METHODS}
                WHERE $1::boolean OR m.active = TRUE
                ORDER BY m.slug
                """,
                include_inactive,
            )
        return [self._row_to_method(row) for row in rows]

    async def contexts_by_method_ids(
        self,
        method_ids: list[int],
    ) -> dict[int, list[MethodRegulatoryContext]]:
        if not method_ids:
            return {}

        pool = await get_pool()
        async with pool.acquire() as conn:
            context_rows = await conn.fetch(self._SELECT_CONTEXTS, method_ids)

        contexts_by_method: dict[int, list[MethodRegulatoryContext]] = defaultdict(list)
        for row in context_rows:
            contexts_by_method[row["method_id"]].append(self._row_to_context(row))
        return dict(contexts_by_method)

    @staticmethod
    def _row_to_method(row) -> Method:
        routes = row["routes_applicable"]
        if isinstance(routes, str):
            routes = json.loads(routes) if routes else None

        embedding = row["embedding_json"]
        if isinstance(embedding, str):
            embedding = json.loads(embedding) if embedding else None

        return Method(
            id=row["id"],
            slug=row["slug"],
            active=row["active"],
            name=parse_localized_str(row["name"]),
            description=parse_localized_str(row["description"]),
            replacement_rationale=row["replacement_rationale"],
            reduction_rationale=row["reduction_rationale"],
            refinement_rationale=row["refinement_rationale"],
            text_for_embedding=row["text_for_embedding"],
            keywords=parse_localized_str_list(row["keywords"]),
            embedding_json=embedding,
            created_at=row["created_at"],
            updated_at=row["updated_at"],
            endpoint_category=row["endpoint_category"],
            routes_applicable=routes,
            study_domain=row["study_domain"],
            oecd_ref=row["oecd_ref"],
            ncit_id=row.get("ncit_id"),
            source_citation=row.get("source_citation"),
            source_doc_id=row.get("source_doc_id"),
            source_url=row.get("source_url"),
            source_db=row["source_db"],
        )

    @staticmethod
    def _norm_vocab(value: str | None) -> str | None:
        if value is None:
            return None
        text = str(value).strip()
        return text.lower() if text else None

    @staticmethod
    def _row_to_context(row) -> MethodRegulatoryContext:
        return MethodRegulatoryContext(
            jurisdiction=MethodRepository._norm_vocab(row["jurisdiction"]),
            validation_status=MethodRepository._norm_vocab(row["validation_status"]),
            regulation_status=MethodRepository._norm_vocab(row["regulation_status"]),
            regulation_date=row["regulation_date"],
            regulation_purpose=row["regulation_purpose"],
            regulatory_body=row["regulatory_body"],
            regulatory_doc_id=row["regulatory_doc_id"],
            regulatory_citation=row["regulatory_citation"],
            regulatory_url=row.get("regulatory_url"),
            notes=row["notes"],
        )
