"""User system models — magic-link auth (F08)."""

from datetime import datetime

from pydantic import BaseModel, EmailStr, Field


class User(BaseModel):
    id: int
    email: EmailStr
    created_at: datetime
    last_seen_at: datetime


class AuthStatusResponse(BaseModel):
    """Public flag endpoint — tells the frontend whether to show user UI."""

    enabled: bool


class MagicLinkRequest(BaseModel):
    email: EmailStr


class MagicLinkResponse(BaseModel):
    message: str
    # Present only in development when no email provider is configured,
    # so the magic link can be opened manually.
    dev_login_link: str | None = None


class MagicLinkVerifyRequest(BaseModel):
    token: str = Field(min_length=1)


class AuthSessionResponse(BaseModel):
    token: str
    user: User
