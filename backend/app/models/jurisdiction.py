"""Jurisdiction vocabulary helpers (localized labels + legacy filter codes)."""

from __future__ import annotations

from typing import Any, Literal

from app.models.i18n import LocalizedStr, localized_str, parse_localized_str

JurisdictionCode = Literal["brazil", "eu", "us", "oecd"]

JURISDICTION_CODES: tuple[JurisdictionCode, ...] = ("brazil", "eu", "us", "oecd")

JURISDICTION_BY_CODE: dict[JurisdictionCode, LocalizedStr] = {
    "brazil": localized_str("Brazil", "Brasil"),
    "eu": localized_str("EU", "UE"),
    "us": localized_str("US", "EUA"),
    "oecd": localized_str("OECD", "OCDE"),
}


def jurisdiction_for_code(code: str) -> LocalizedStr | None:
    key = code.strip().lower()
    if key in JURISDICTION_BY_CODE:
        return JURISDICTION_BY_CODE[key]  # type: ignore[index]
    return None


def parse_jurisdiction(value: Any) -> LocalizedStr:
    if isinstance(value, str):
        text = value.strip()
        mapped = jurisdiction_for_code(text) if text else None
        if mapped is not None:
            return mapped
    return parse_localized_str(value)


def jurisdiction_code(value: LocalizedStr | str | None) -> JurisdictionCode | None:
    if value is None:
        return None
    if isinstance(value, str):
        key = value.strip().lower()
        if key in JURISDICTION_BY_CODE:
            return key  # type: ignore[return-value]
        value = parse_jurisdiction(value)
    for code, labels in JURISDICTION_BY_CODE.items():
        if (
            value.en_us.casefold() == labels.en_us.casefold()
            or value.pt_br.casefold() == labels.pt_br.casefold()
        ):
            return code
    return None


def jurisdiction_matches(
    stored: LocalizedStr | str | None,
    filter_code: str,
) -> bool:
    expected = jurisdiction_for_code(filter_code)
    if expected is None or stored is None:
        return False
    actual = parse_jurisdiction(stored)
    return (
        actual.en_us.casefold() == expected.en_us.casefold()
        or actual.pt_br.casefold() == expected.pt_br.casefold()
    )
