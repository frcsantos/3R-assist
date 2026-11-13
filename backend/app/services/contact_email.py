import logging

import httpx

from app.config import Settings

logger = logging.getLogger(__name__)

RESEND_URL = "https://api.resend.com/emails"
TIMEOUT_SECONDS = 10.0


def is_configured(settings: Settings) -> bool:
    return bool(
        settings.email_provider_api_key
        and settings.email_from_address
        and settings.contact_to_email
    )


def _email_subject(subject: str | None) -> str:
    clean = " ".join((subject or "").split())
    return f"[Assist3R] {clean}" if clean else "Assist3R contact message"


async def forward_contact_message(
    settings: Settings,
    *,
    message: str,
    page_url: str,
    subject: str | None = None,
) -> bool:
    """Forward a contact-form message through Resend. Never raises."""
    if not is_configured(settings):
        return False

    payload = {
        "from": settings.email_from_address,
        "to": [settings.contact_to_email],
        "subject": _email_subject(subject),
        "text": f"{message}\n\n---\nSent from: {page_url}",
    }
    try:
        async with httpx.AsyncClient(timeout=TIMEOUT_SECONDS) as client:
            response = await client.post(
                RESEND_URL,
                json=payload,
                headers={"Authorization": f"Bearer {settings.email_provider_api_key}"},
            )
        if response.status_code >= 400:
            logger.warning(
                "Resend rejected contact email: %s %s",
                response.status_code,
                response.text[:300],
            )
            return False
        return True
    except httpx.HTTPError:
        logger.exception("Could not reach Resend for contact email")
        return False
