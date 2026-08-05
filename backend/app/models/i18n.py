"""Localized string / list types keyed by BCP-47 locale codes."""

from __future__ import annotations

import json
from typing import Any, Literal

from pydantic import BaseModel, ConfigDict, Field, field_validator

LocaleCode = Literal["en-us", "pt-br"]

LOCALE_CODES: tuple[LocaleCode, ...] = ("en-us", "pt-br")
DEFAULT_LOCALE: LocaleCode = "en-us"

_LANG_TO_LOCALE: dict[str, LocaleCode] = {
    "en": "en-us",
    "en-us": "en-us",
    "en_US": "en-us",
    "pt": "pt-br",
    "pt-br": "pt-br",
    "pt_BR": "pt-br",
}


def resolve_locale(lang: str | None) -> LocaleCode:
    if not lang:
        return DEFAULT_LOCALE
    key = lang.strip().lower().replace("_", "-")
    if key in _LANG_TO_LOCALE:
        return _LANG_TO_LOCALE[key]
    short = key.split("-", 1)[0]
    return _LANG_TO_LOCALE.get(short, DEFAULT_LOCALE)


class LocalizedStr(BaseModel):
    """Bilingual text: ``{"en-us": "...", "pt-br": "..."}``."""

    model_config = ConfigDict(
        populate_by_name=True,
        extra="ignore",
        serialize_by_alias=True,
    )

    en_us: str = Field(alias="en-us")
    pt_br: str = Field(alias="pt-br")

    def pick(self, lang: str | None = None) -> str:
        locale = resolve_locale(lang)
        data = self.model_dump(by_alias=True)
        text = data.get(locale) or data.get(DEFAULT_LOCALE) or ""
        return text if isinstance(text, str) else str(text)

    def joined(self, sep: str = " ") -> str:
        return sep.join(part for part in (self.en_us, self.pt_br) if part)


class LocalizedStrList(BaseModel):
    """Bilingual string lists: ``{"en-us": [...], "pt-br": [...]}``."""

    model_config = ConfigDict(
        populate_by_name=True,
        extra="ignore",
        serialize_by_alias=True,
    )

    en_us: list[str] = Field(default_factory=list, alias="en-us")
    pt_br: list[str] = Field(default_factory=list, alias="pt-br")

    @field_validator("en_us", "pt_br", mode="before")
    @classmethod
    def _coerce_list(cls, value: Any) -> list[str]:
        if value is None:
            return []
        if isinstance(value, str):
            text = value.strip()
            return [text] if text else []
        if not isinstance(value, list):
            return []
        items: list[str] = []
        for item in value:
            if item is None:
                continue
            text = str(item).strip()
            if text:
                items.append(text)
        return items

    def pick(self, lang: str | None = None) -> list[str]:
        locale = resolve_locale(lang)
        data = self.model_dump(by_alias=True)
        values = data.get(locale) or data.get(DEFAULT_LOCALE) or []
        return list(values) if isinstance(values, list) else []

    def all_values(self) -> list[str]:
        return [*self.en_us, *self.pt_br]


def localized_str(en: str, pt: str | None = None) -> LocalizedStr:
    text = (en or "").strip()
    other = (pt if pt is not None else en) or text
    return LocalizedStr.model_validate({"en-us": text, "pt-br": str(other).strip()})


def localized_str_list(
    en: list[str] | None = None,
    pt: list[str] | None = None,
) -> LocalizedStrList:
    return LocalizedStrList.model_validate(
        {"en-us": list(en or []), "pt-br": list(pt or [])}
    )


def parse_localized_str(value: Any, *, required: bool = True) -> LocalizedStr | None:
    if value is None:
        if required:
            raise ValueError("Localized string is required")
        return None
    if isinstance(value, LocalizedStr):
        return value
    if isinstance(value, str):
        value = json.loads(value) if value.strip() else None
        if value is None:
            if required:
                raise ValueError("Localized string is required")
            return None
    if isinstance(value, dict):
        en = value.get("en-us", value.get("en_us", value.get("en")))
        pt = value.get("pt-br", value.get("pt_br", value.get("pt", en)))
        if en is None and pt is None:
            if required:
                raise ValueError("Localized string requires en-us / pt-br")
            return None
        return localized_str(str(en or pt or ""), str(pt if pt is not None else en or ""))
    raise TypeError(f"Unsupported localized string value: {type(value)!r}")


def parse_localized_str_list(value: Any) -> LocalizedStrList:
    if value is None:
        return LocalizedStrList()
    if isinstance(value, LocalizedStrList):
        return value
    if isinstance(value, str):
        value = json.loads(value) if value.strip() else {}
    if isinstance(value, dict):
        return LocalizedStrList.model_validate(
            {
                "en-us": value.get(
                    "en-us", value.get("en_us", value.get("en", []))
                ),
                "pt-br": value.get(
                    "pt-br", value.get("pt_br", value.get("pt", []))
                ),
            }
        )
    if isinstance(value, list):
        return localized_str_list(value, value)
    raise TypeError(f"Unsupported localized string list value: {type(value)!r}")
