from fastapi import APIRouter
from pydantic import BaseModel

from app.services import vocabulary

router = APIRouter(prefix="/vocabularies", tags=["vocabularies"])


class ApplicationItem(BaseModel):
    id: int
    slug: str
    name: dict
    description: dict
    sort_order: int


class ApplicationsResponse(BaseModel):
    items: list[ApplicationItem]


@router.get("/applications", response_model=ApplicationsResponse)
async def list_applications() -> ApplicationsResponse:
    await vocabulary.ensure_applications_loaded()
    return ApplicationsResponse(
        items=[
            ApplicationItem(
                id=row.id,
                slug=row.slug,
                name=row.name,
                description=row.description,
                sort_order=row.sort_order,
            )
            for row in vocabulary.application_rows()
        ]
    )


class RouteItem(BaseModel):
    id: int
    slug: str
    name: dict
    description: dict
    sort_order: int


class RoutesResponse(BaseModel):
    items: list[RouteItem]


@router.get("/routes", response_model=RoutesResponse)
async def list_routes() -> RoutesResponse:
    from app.db.connection import get_pool

    pool = await get_pool()
    async with pool.acquire() as conn:
        records = await conn.fetch(
            "SELECT id, slug, name, description, sort_order "
            "FROM routes WHERE active ORDER BY sort_order, id"
        )
    return RoutesResponse(
        items=[
            RouteItem(
                id=r["id"],
                slug=r["slug"],
                name=r["name"] or {},
                description=r["description"] or {},
                sort_order=r["sort_order"] or 0,
            )
            for r in records
        ]
    )


class SpeciesItem(BaseModel):
    id: int
    slug: str
    name: dict
    scientific_name: str | None
    taxon_group: str | None
    sort_order: int


class SpeciesResponse(BaseModel):
    items: list[SpeciesItem]


@router.get("/species", response_model=SpeciesResponse)
async def list_species() -> SpeciesResponse:
    from app.db.connection import get_pool

    pool = await get_pool()
    async with pool.acquire() as conn:
        records = await conn.fetch(
            "SELECT id, slug, name, scientific_name, taxon_group, sort_order "
            "FROM species WHERE active ORDER BY sort_order, id"
        )
    return SpeciesResponse(
        items=[
            SpeciesItem(
                id=r["id"],
                slug=r["slug"],
                name=r["name"] or {},
                scientific_name=r["scientific_name"],
                taxon_group=r["taxon_group"],
                sort_order=r["sort_order"] or 0,
            )
            for r in records
        ]
    )


class EnumTermItem(BaseModel):
    code: str
    name: dict
    description: dict
    sort_order: int


class EnumTermsResponse(BaseModel):
    domains: dict[str, list[EnumTermItem]]


@router.get("/enums", response_model=EnumTermsResponse)
async def list_enum_terms() -> EnumTermsResponse:
    from app.db.connection import get_pool

    pool = await get_pool()
    async with pool.acquire() as conn:
        records = await conn.fetch(
            "SELECT domain, code, name, description, sort_order "
            "FROM enum_terms WHERE active ORDER BY domain, sort_order, code"
        )
    domains: dict[str, list[EnumTermItem]] = {}
    for r in records:
        domains.setdefault(r["domain"], []).append(
            EnumTermItem(
                code=r["code"],
                name=r["name"] or {},
                description=r["description"] or {},
                sort_order=r["sort_order"] or 0,
            )
        )
    return EnumTermsResponse(domains=domains)
