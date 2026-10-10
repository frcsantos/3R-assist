"""Auth routes (F08 magic link) — gated behind USER_SYSTEM_ENABLED.

While the user system is disabled (default), every endpoint except
`GET /auth/status` returns 404, exactly as if the routes did not exist.
`GET /auth/status` always responds so the frontend can hide sign-in UI
without hard-coding the flag.
"""

from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, Request, Response
from fastapi.responses import JSONResponse

from app.api.deps import (
    get_auth_service,
    get_current_user,
    get_user_repository,
)
from app.api.errors import error_response
from app.config import get_settings
from app.models.user import (
    AuthSessionResponse,
    AuthStatusResponse,
    MagicLinkRequest,
    MagicLinkResponse,
    MagicLinkVerifyRequest,
    User,
)
from app.repositories.users import UserRepository
from app.services.auth import AuthError, AuthService

router = APIRouter(prefix="/auth", tags=["auth"])


def _database_unavailable(exc: Exception) -> JSONResponse:
    return error_response(
        status_code=503,
        code="DATABASE_UNAVAILABLE",
        message="User database is not configured.",
        detail={"type": type(exc).__name__, "reason": str(exc)},
    )


async def require_user_system_enabled() -> None:
    if not get_settings().user_system_enabled:
        raise HTTPException(status_code=404, detail="Not Found")


@router.get("/status", response_model=AuthStatusResponse)
async def auth_status() -> AuthStatusResponse:
    """Public flag endpoint — reports whether the user system is available."""
    return AuthStatusResponse(enabled=get_settings().user_system_enabled)


@router.post(
    "/magic-link",
    response_model=MagicLinkResponse,
    dependencies=[Depends(require_user_system_enabled)],
)
async def request_magic_link(
    payload: MagicLinkRequest,
    auth: AuthService = Depends(get_auth_service),
    repository: UserRepository = Depends(get_user_repository),
) -> MagicLinkResponse | JSONResponse:
    settings = get_settings()
    if not settings.database_url:
        return error_response(
            status_code=503,
            code="DATABASE_UNAVAILABLE",
            message="User database is not configured.",
        )
    try:
        user = await repository.get_or_create_user(payload.email)
        token = auth.issue_magic_link_token(user.email)
        await repository.create_magic_link_token(
            user.id, auth.hash_token(token)
        )
    except ValueError as exc:
        return _database_unavailable(exc)

    # Email delivery is TBD (Phase 2, Phase B). Until an email provider is
    # wired up, surface the link in the API response for development so the
    # flow can be exercised end to end.
    can_email = bool(settings.email_provider_api_key and settings.email_from_address)
    dev_link = None
    if settings.app_env == "development" or not can_email:
        dev_link = f"{settings.app_base_url}/auth?token={token}"

    message = (
        "If that email address exists, a sign-in link is on its way."
        if can_email
        else "Sign-in links are not being emailed yet — use the development link."
    )
    return MagicLinkResponse(message=message, dev_login_link=dev_link)


@router.post(
    "/verify",
    response_model=AuthSessionResponse,
    dependencies=[Depends(require_user_system_enabled)],
)
async def verify_magic_link(
    payload: MagicLinkVerifyRequest,
    auth: AuthService = Depends(get_auth_service),
    repository: UserRepository = Depends(get_user_repository),
) -> AuthSessionResponse | JSONResponse:
    settings = get_settings()
    if not settings.database_url:
        return error_response(
            status_code=503,
            code="DATABASE_UNAVAILABLE",
            message="User database is not configured.",
        )
    try:
        email = auth.verify_magic_link_token(payload.token)
    except AuthError:
        return error_response(
            status_code=401,
            code="INVALID_TOKEN",
            message="This sign-in link is invalid or has expired.",
        )

    try:
        user_id = await repository.consume_magic_link_token(
            auth.hash_token(payload.token)
        )
        if user_id is None:
            return error_response(
                status_code=401,
                code="INVALID_TOKEN",
                message="This sign-in link is invalid or has expired.",
            )
        session_token = auth.issue_session_token(user_id)
        await repository.create_session(user_id, auth.hash_token(session_token))
        user = await repository.get_user(user_id)
    except ValueError as exc:
        return _database_unavailable(exc)

    if user is None:
        return error_response(
            status_code=401,
            code="INVALID_TOKEN",
            message="This sign-in link is invalid or has expired.",
        )
    return AuthSessionResponse(token=session_token, user=user)


@router.get("/me", response_model=User)
async def me(user: User = Depends(get_current_user)) -> User:
    return user


@router.post(
    "/logout",
    dependencies=[Depends(require_user_system_enabled)],
)
async def logout(
    request: Request,
    auth: AuthService = Depends(get_auth_service),
    repository: UserRepository = Depends(get_user_repository),
) -> Response:
    header = request.headers.get("Authorization", "")
    token = header.removeprefix("Bearer").strip()
    if token:
        try:
            await repository.revoke_session(auth.hash_token(token))
        except ValueError as exc:
            return _database_unavailable(exc)
    return Response(status_code=204)
