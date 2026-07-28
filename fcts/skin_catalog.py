from __future__ import annotations

import json
import re
import shlex
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from project_paths import CONFIG_DIR, FONT_DIR, PROJECT_ROOT, RANKCARD_DIR


ROOT = PROJECT_ROOT
STORAGE_PATH = CONFIG_DIR / "storage.json"
QUEUE_ROOT = RANKCARD_DIR / "upload"
FONT_ROOT = FONT_DIR
QUEUE_ID_PATTERN = re.compile(r"^t([1-9]\d*)$", re.IGNORECASE)


@dataclass(frozen=True)
class SkinSearch:
    page: int = 1
    skin_id: str | None = None
    unlock_type: str | None = None
    keyword: str | None = None
    terms: tuple[str, ...] = ()


def _skin_number(value: Any) -> int:
    text = str(value).strip().lower()
    if text.startswith("t"):
        text = text[1:]
    return int(text)


def _normalize_storage_skin(value: dict[str, Any]) -> dict[str, Any]:
    skin = dict(value)
    skin["id"] = str(skin.get("id", "")).strip()
    skin["name"] = str(skin.get("name", "")).strip()
    skin["desc"] = str(skin.get("desc", "")).strip()
    skin["unlock_type"] = str(skin.get("unlock_type", "")).strip().lower()
    skin["keyword"] = str(skin.get("keyword", "")).strip()
    return skin


def load_storage() -> list[dict[str, Any]]:
    with STORAGE_PATH.open("r", encoding="utf-8") as file:
        raw = json.load(file)

    if not isinstance(raw, dict):
        raise ValueError("config/storage.json must contain a JSON object")

    skins = []
    for key, value in raw.items():
        if not isinstance(value, dict):
            raise ValueError(f"{key} must contain a skin object")
        skin = _normalize_storage_skin(value)
        skin["_key"] = key
        skins.append(skin)

    return sorted(skins, key=lambda skin: _skin_number(skin["id"]))


def storage_rows(option: str | None = None) -> list[list[str]]:
    rows = []
    normalized_option = (option or "").strip().casefold()
    for skin in load_storage():
        if normalized_option not in {"", "all"}:
            keywords = {
                keyword.casefold()
                for keyword in re.split(r"[,;/\s]+", skin["keyword"])
                if keyword
            }
            if normalized_option not in keywords:
                continue
        rows.append([
            skin["id"],
            skin["name"],
            skin["desc"],
            skin["unlock_type"],
            str(skin.get("unlock_val", "")),
        ])
    return rows


def normalize_queue_id(value: str) -> str:
    match = QUEUE_ID_PATTERN.fullmatch(str(value).strip())
    if match is None:
        raise ValueError("Queue IDs must use the t<number> format.")
    return f"t{int(match.group(1))}"


def queue_skin_dir(queue_id: str) -> Path:
    return QUEUE_ROOT / f"skin{normalize_queue_id(queue_id)}"


def load_queue_skin(queue_id: str) -> dict[str, Any] | None:
    normalized_id = normalize_queue_id(queue_id)
    directory = queue_skin_dir(normalized_id)
    path = directory / "skin.json"
    if not path.is_file():
        return None

    with path.open("r", encoding="utf-8") as file:
        raw = json.load(file)

    if not isinstance(raw, dict) or not isinstance(raw.get("skin"), dict):
        raise ValueError(f"{path} has an invalid skin data structure")

    skin = _normalize_storage_skin(raw["skin"])
    skin["id"] = normalized_id
    skin["_font"] = raw.get("font", {})
    skin["_path"] = directory
    return skin


def load_queue() -> list[dict[str, Any]]:
    if not QUEUE_ROOT.is_dir():
        return []

    skins = []
    for directory in QUEUE_ROOT.iterdir():
        if not directory.is_dir() or not directory.name.lower().startswith("skint"):
            continue
        try:
            skin = load_queue_skin(directory.name[4:])
        except (OSError, ValueError, json.JSONDecodeError):
            continue
        if skin is not None:
            skins.append(skin)

    return sorted(skins, key=lambda skin: _skin_number(skin["id"]))


def next_queue_id() -> str:
    numbers = []
    if QUEUE_ROOT.is_dir():
        for directory in QUEUE_ROOT.iterdir():
            if not directory.is_dir():
                continue
            match = re.fullmatch(r"skint([1-9]\d*)", directory.name, re.IGNORECASE)
            if match:
                numbers.append(int(match.group(1)))
    return f"t{max(numbers, default=0) + 1}"


def font_families() -> list[str]:
    if not FONT_ROOT.is_dir():
        return []
    return sorted(
        directory.name
        for directory in FONT_ROOT.iterdir()
        if (
            directory.is_dir()
            and not directory.name.casefold().startswith("license")
            and (directory / "name.ttf").is_file()
            and (directory / "xp.ttf").is_file()
        )
    )


def format_unlock_condition(skin: dict[str, Any], user) -> str:
    from fcts import i18n_runtime as i18n

    unlock_type = str(skin.get("unlock_type", "none")).strip().casefold()
    value = skin.get("unlock_val", "")

    if unlock_type == "level":
        try:
            value = int(value)
        except (TypeError, ValueError):
            pass
        return i18n.t(user, "skin.unlock.level", value=value)
    if unlock_type == "money":
        try:
            value = f"{int(value):,d}"
        except (TypeError, ValueError):
            value = str(value)
        return i18n.t(user, "skin.unlock.money", value=value)
    if unlock_type in {"code", "game", "none"}:
        return i18n.t(user, f"skin.unlock.{unlock_type}")
    return unlock_type or "-"


def parse_search(query: str | None) -> SkinSearch:
    text = (query or "").strip()
    if not text:
        return SkinSearch()

    try:
        tokens = shlex.split(text)
    except ValueError:
        tokens = text.split()

    page = 1
    skin_id = None
    unlock_type = None
    keyword = None
    terms: list[str] = []

    for token in tokens:
        key, separator, value = token.partition(":")
        if not separator:
            key, separator, value = token.partition("=")

        normalized_key = key.casefold()
        value = value.strip()
        if separator and normalized_key in {"page", "p", "페이지"}:
            if not value.isdigit() or int(value) < 1:
                raise ValueError("Page must be a positive integer.")
            page = int(value)
        elif separator and normalized_key in {"id", "번호"}:
            try:
                skin_id = (
                    normalize_queue_id(value)
                    if value.casefold().startswith("t")
                    else str(int(value))
                )
            except ValueError as error:
                raise ValueError("ID must be a number or a t-prefixed queue ID.") from error
        elif separator and normalized_key in {"type", "unlock", "유형", "해금"}:
            unlock_type = value.casefold()
        elif separator and normalized_key in {"keyword", "key", "키워드"}:
            keyword = value.casefold()
        elif token.casefold() != "all":
            terms.append(token.casefold())

    # Backward compatibility: "?skin pokemon 2" means keyword pokemon, page 2.
    if terms and terms[-1].isdigit():
        page = int(terms.pop())
        if page < 1:
            raise ValueError("Page must be a positive integer.")

    return SkinSearch(
        page=page,
        skin_id=skin_id,
        unlock_type=unlock_type,
        keyword=keyword,
        terms=tuple(terms),
    )


def filter_skins(
    skins: list[dict[str, Any]],
    query: str | None,
) -> tuple[list[dict[str, Any]], int]:
    search = parse_search(query)
    result = []

    for skin in skins:
        candidate_id = str(skin.get("id", "")).strip().casefold()
        comparable_id = (
            candidate_id
            if candidate_id.startswith("t")
            else str(int(candidate_id))
        )
        unlock_type = str(skin.get("unlock_type", "")).casefold()
        keyword = str(skin.get("keyword", "")).casefold()
        searchable = " ".join(
            str(skin.get(field, ""))
            for field in ("id", "name", "desc", "unlock_type", "unlock_val", "keyword",
                          "creater", "date")
        ).casefold()

        if search.skin_id and comparable_id != search.skin_id.casefold():
            continue
        if search.unlock_type and unlock_type != search.unlock_type:
            continue
        if search.keyword and search.keyword not in keyword:
            continue
        if any(term not in searchable for term in search.terms):
            continue
        result.append(skin)

    return result, search.page
