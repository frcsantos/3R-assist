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
        m.animal_use, m.test_system,
        m.endpoints,
        (
          SELECT COALESCE(array_agg(ep.slug ORDER BY u.ord), '{}'::text[])
          FROM unnest(COALESCE(m.endpoints, '{}'::int[]))
            WITH ORDINALITY AS u(eid, ord)
          JOIN endpoints ep ON ep.id = u.eid
        ) AS endpoint_codes,
        (
          SELECT COALESCE(jsonb_agg(ep.name ORDER BY u.ord), '[]'::jsonb)
          FROM unnest(COALESCE(m.endpoints, '{}'::int[]))
            WITH ORDINALITY AS u(eid, ord)
          JOIN endpoints ep ON ep.id = u.eid
        ) AS endpoint_names,
        m.routes_applicable,
        (
          SELECT COALESCE(array_agg(rt.slug ORDER BY u.ord), '{}'::text[])
          FROM unnest(COALESCE(m.routes_applicable, '{}'::int[]))
            WITH ORDINALITY AS u(rid, ord)
          JOIN routes rt ON rt.id = u.rid
        ) AS route_codes,
        (
          SELECT COALESCE(jsonb_agg(rt.name ORDER BY u.ord), '[]'::jsonb)
          FROM unnest(COALESCE(m.routes_applicable, '{}'::int[]))
            WITH ORDINALITY AS u(rid, ord)
          JOIN routes rt ON rt.id = u.rid
        ) AS route_names,
        m.application_ids,
        (
          SELECT COALESCE(array_agg(ap.slug ORDER BY u.ord), '{}'::text[])
          FROM unnest(COALESCE(m.application_ids, '{}'::int[]))
            WITH ORDINALITY AS u(aid, ord)
          JOIN applications ap ON ap.id = u.aid
        ) AS application_codes,
        (
          SELECT COALESCE(jsonb_agg(ap.name ORDER BY u.ord), '[]'::jsonb)
          FROM unnest(COALESCE(m.application_ids, '{}'::int[]))
            WITH ORDINALITY AS u(aid, ord)
          JOIN applications ap ON ap.id = u.aid
        ) AS application_names,
        m.oecd_ref, m.ncit_id,
        COALESCE(
            NULLIF(BTRIM(m.source_citation), ''),
            NULLIF(BTRIM(sd.doc_citation->>'en-us'), ''),
            sd.doc_citation->>'pt-br'
        ) AS source_citation,
        m.source_doc_id,
        sd.url AS source_url,
        m.source_db,
        m.validation_status,
        m.validation_doc_id,
        vd.url AS validation_url,
        m.replacement_rationale, m.reduction_rationale, m.refinement_rationale,
        m.keywords, m.text_for_embedding, m.embedding_json,
        m.created_at, m.updated_at
    """

    _FROM_METHODS = """
        FROM methods m
        LEFT JOIN documents sd ON sd.id = m.source_doc_id
        LEFT JOIN documents vd ON vd.id = m.validation_doc_id
    """

    _SELECT_ACTIVE = f"""
        SELECT {_SELECT_COLUMNS}
        {_FROM_METHODS}
        WHERE m.active = TRUE
        ORDER BY m.slug
    """

    _SELECT_CONTEXTS = """
        SELECT
            mrc.id, mrc.method_id, mrc.jurisdiction,
            mrc.regulatory_status, mrc.regulatory_date, mrc.regulatory_endpoints,
            (
              SELECT COALESCE(
                jsonb_agg(e.name ORDER BY u.ord),
                '[]'::jsonb
              )
              FROM unnest(COALESCE(mrc.regulatory_endpoints, '{}'::int[]))
                WITH ORDINALITY AS u(eid, ord)
              JOIN endpoints e ON e.id = u.eid
            ) AS regulatory_endpoint_names,
            mrc.endpoint_quote,
            mrc.regulatory_body, mrc.regulatory_doc_id,
            CASE
              WHEN mrc.regulatory_citation IS NOT NULL
               AND (
                 NULLIF(BTRIM(mrc.regulatory_citation->>'en-us'), '') IS NOT NULL
                 OR NULLIF(BTRIM(mrc.regulatory_citation->>'pt-br'), '') IS NOT NULL
               )
              THEN mrc.regulatory_citation
              ELSE rd.doc_citation
            END AS regulatory_citation,
            rd.url AS regulatory_url,
            mrc.notes
        FROM regulations mrc
        LEFT JOIN documents rd ON rd.id = mrc.regulatory_doc_id
        WHERE mrc.method_id = ANY($1::int[])
        ORDER BY mrc.method_id, mrc.jurisdiction->>'en-us'
    """

    async def list_active(self) -> list[Method]:
        methods, _ = await self.list_active_with_contexts()
        return methods

    async def list_active_with_contexts(
        self,
    ) -> tuple[list[Method], dict[int, list[MethodRegulatoryContext]]]:
        return await self.list_with_contexts(active_only=True)

    async def list_with_contexts(
        self,
        *,
        active_only: bool = False,
    ) -> tuple[list[Method], dict[int, list[MethodRegulatoryContext]]]:
        pool = await get_pool()
        async with pool.acquire() as conn:
            if active_only:
                rows = await conn.fetch(self._SELECT_ACTIVE)
            else:
                rows = await conn.fetch(
                    f"""
                    SELECT {self._SELECT_COLUMNS}
                    {self._FROM_METHODS}
                    ORDER BY m.slug
                    """
                )
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

        test_system = row.get("test_system")
        if isinstance(test_system, str):
            test_system = json.loads(test_system) if test_system else None

        embedding = row["embedding_json"]
        if isinstance(embedding, str):
            embedding = json.loads(embedding) if embedding else None

        return Method(
            id=row["id"],
            slug=row["slug"],
            active=row["active"],
            name=parse_localized_str(row["name"]),
            description=parse_localized_str(row["description"]),
            replacement_rationale=parse_localized_str(
                row["replacement_rationale"], required=False
            ),
            reduction_rationale=parse_localized_str(
                row["reduction_rationale"], required=False
            ),
            refinement_rationale=parse_localized_str(
                row["refinement_rationale"], required=False
            ),
            text_for_embedding=row["text_for_embedding"],
            keywords=parse_localized_str_list(row["keywords"]),
            embedding_json=embedding,
            created_at=row["created_at"],
            updated_at=row["updated_at"],
            endpoints=row["endpoints"] or [],
            endpoint_codes=list(row["endpoint_codes"] or []),
            endpoint_names=row.get("endpoint_names") or [],
            routes_applicable=routes,
            route_codes=list(row.get("route_codes") or []),
            route_names=row.get("route_names") or [],
            application_ids=row.get("application_ids") or [],
            application_codes=list(row.get("application_codes") or []),
            application_names=row.get("application_names") or [],
            animal_use=row.get("animal_use"),
            test_system=test_system,
            oecd_ref=row["oecd_ref"],
            ncit_id=row.get("ncit_id"),
            source_citation=row.get("source_citation"),
            source_doc_id=row.get("source_doc_id"),
            source_url=row.get("source_url"),
            source_db=row["source_db"],
            validation_status=MethodRepository._norm_vocab(row["validation_status"])
            or "not_evaluated",
            validation_doc_id=row.get("validation_doc_id"),
            validation_url=row.get("validation_url"),
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
            id=row["id"],
            jurisdiction=row["jurisdiction"],
            regulatory_status=MethodRepository._norm_vocab(row["regulatory_status"]),
            regulatory_date=row["regulatory_date"],
            regulatory_endpoints=row["regulatory_endpoints"],
            regulatory_endpoint_names=row["regulatory_endpoint_names"] or [],
            endpoint_quote=row["endpoint_quote"],
            regulatory_body=row["regulatory_body"],
            regulatory_doc_id=row["regulatory_doc_id"],
            regulatory_citation=row["regulatory_citation"],
            regulatory_url=row.get("regulatory_url"),
            notes=row["notes"],
        )
