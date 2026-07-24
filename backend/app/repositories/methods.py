"""MethodRepository — query logic for curated methods."""

from __future__ import annotations

import json
from collections import defaultdict

from app.db.connection import get_pool
from app.models.method import Method, MethodRegulatoryContext


class MethodRepository:
    _SELECT_COLUMNS = """
        id, slug, active, name_en, name_pt, description_en, description_pt,
        endpoint_category, routes_applicable, study_domain,
        oecd_ref, ncit_id, source_db,
        replacement_rationale, reduction_rationale, refinement_rationale,
        keywords_en, keywords_pt, text_for_embedding, embedding_json,
        created_at, updated_at
    """

    _SELECT_ACTIVE = f"""
        SELECT {_SELECT_COLUMNS}
        FROM methods
        WHERE active = TRUE
        ORDER BY slug
    """

    _SELECT_CONTEXTS = """
        SELECT
            method_id, study_domain, jurisdiction, validation_status,
            regulation_status, regulation_date, regulation_purpose,
            regulatory_body, regulatory_url, notes
        FROM method_regulatory_contexts
        WHERE method_id = ANY($1::int[])
        ORDER BY method_id, study_domain, jurisdiction
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
                FROM methods
                WHERE oecd_ref IS NOT NULL
                  AND lower(regexp_replace(trim(oecd_ref), '\\s+', ' ', 'g'))
                      = lower($1)
                  AND ($2::boolean OR active = TRUE)
                ORDER BY slug
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
                FROM methods
                WHERE $1::boolean OR active = TRUE
                ORDER BY slug
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
    def _parse_str_list(value) -> list[str]:
        if value is None:
            return []
        if isinstance(value, str):
            value = json.loads(value) if value else []
        return list(value)

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
            name_en=row["name_en"],
            name_pt=row["name_pt"],
            description_en=row["description_en"],
            description_pt=row["description_pt"],
            replacement_rationale=row["replacement_rationale"],
            reduction_rationale=row["reduction_rationale"],
            refinement_rationale=row["refinement_rationale"],
            text_for_embedding=row["text_for_embedding"],
            keywords_en=MethodRepository._parse_str_list(row["keywords_en"]),
            keywords_pt=MethodRepository._parse_str_list(row["keywords_pt"]),
            embedding_json=embedding,
            created_at=row["created_at"],
            updated_at=row["updated_at"],
            endpoint_category=row["endpoint_category"],
            routes_applicable=routes,
            study_domain=row["study_domain"],
            oecd_ref=row["oecd_ref"],
            ncit_id=row.get("ncit_id"),
            source_db=row["source_db"],
        )

    @staticmethod
    def _row_to_context(row) -> MethodRegulatoryContext:
        return MethodRegulatoryContext(
            study_domain=row["study_domain"],
            jurisdiction=row["jurisdiction"],
            validation_status=row["validation_status"],
            regulation_status=row["regulation_status"],
            regulation_date=row["regulation_date"],
            regulation_purpose=row["regulation_purpose"],
            regulatory_body=row["regulatory_body"],
            regulatory_url=row["regulatory_url"],
            notes=row["notes"],
        )
