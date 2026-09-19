"""Persistence and catalog helpers for NELG Plus (command ID 52)."""

from __future__ import annotations

import json
import sqlite3
from contextlib import closing
from datetime import datetime, timedelta

from project_paths import CONFIG_DIR, DATA_DIR


DB_PATH = DATA_DIR / "nelgp.db"
CATALOG_PATH = CONFIG_DIR / "nelgp.json"


def _kst_now() -> str:
    return (datetime.utcnow() + timedelta(hours=9)).strftime("%Y/%m/%d %H:%M:%S")


def initSetting() -> None:
    """Create the normalized NELG+ achievement database."""
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    with closing(sqlite3.connect(DB_PATH)) as connection:
        connection.execute(
            """
            CREATE TABLE IF NOT EXISTS users (
                user_id INTEGER PRIMARY KEY,
                joined_at TEXT NOT NULL
            )
            """
        )
        connection.execute(
            """
            CREATE TABLE IF NOT EXISTS achievement_unlocks (
                user_id INTEGER NOT NULL,
                achievement_id INTEGER NOT NULL,
                unlocked_at TEXT NOT NULL,
                PRIMARY KEY (user_id, achievement_id),
                FOREIGN KEY (user_id) REFERENCES users(user_id)
                    ON DELETE CASCADE
            )
            """
        )
        connection.commit()


def ensureUser(user_id: int) -> bool:
    """Ensure a NELG+ profile exists and return whether it was created."""
    with closing(sqlite3.connect(DB_PATH)) as connection:
        cursor = connection.execute(
            "INSERT OR IGNORE INTO users (user_id, joined_at) VALUES (?, ?)",
            (int(user_id), _kst_now()),
        )
        connection.commit()
        return cursor.rowcount == 1


def unlockAchievement(user_id: int, achievement_id: int) -> bool:
    """Unlock once and return True only for a newly inserted achievement."""
    ensureUser(user_id)
    with closing(sqlite3.connect(DB_PATH)) as connection:
        cursor = connection.execute(
            """
            INSERT OR IGNORE INTO achievement_unlocks
                (user_id, achievement_id, unlocked_at)
            VALUES (?, ?, ?)
            """,
            (int(user_id), int(achievement_id), _kst_now()),
        )
        connection.commit()
        return cursor.rowcount == 1


def achievementState(user_id: int) -> dict[int, str]:
    """Return achievement IDs mapped to completion timestamps."""
    ensureUser(user_id)
    with closing(sqlite3.connect(DB_PATH)) as connection:
        rows = connection.execute(
            """
            SELECT achievement_id, unlocked_at
            FROM achievement_unlocks
            WHERE user_id = ?
            """,
            (int(user_id),),
        ).fetchall()
    return {int(achievement_id): str(unlocked_at) for achievement_id, unlocked_at in rows}


def readJoinTime(user_id: int) -> str:
    ensureUser(user_id)
    with closing(sqlite3.connect(DB_PATH)) as connection:
        row = connection.execute(
            "SELECT joined_at FROM users WHERE user_id = ?",
            (int(user_id),),
        ).fetchone()
    return str(row[0])


def _normalize_color(value) -> int:
    if isinstance(value, int):
        return max(0, min(value, 0xFFFFFF))
    text = str(value or "#A8E6CF").strip().removeprefix("#")
    try:
        return int(text, 16)
    except ValueError as error:
        raise ValueError("NELG+ meta.color must be a hexadecimal color.") from error


def _catalog_items(source):
    if isinstance(source, dict):
        return source.items()
    if isinstance(source, list):
        return ((index + 1, item) for index, item in enumerate(source))
    raise ValueError("NELG+ achievements must be an object or a list.")


def _read_codes(raw_item) -> list[str]:
    raw_codes = raw_item.get("code", raw_item.get("inputCodes", ""))
    if isinstance(raw_codes, list):
        codes = [str(code).strip() for code in raw_codes]
    else:
        codes = [str(raw_codes).strip()]
    return [code for code in codes if code]


def loadCatalog() -> dict:
    """Load and validate the NELG+ achievement and hint catalog."""
    with CATALOG_PATH.open(encoding="utf-8") as catalog_file:
        document = json.load(catalog_file)

    if not isinstance(document, dict):
        raise ValueError("NELG+ catalog root must be an object.")
    meta_source = document.get("meta", {})
    source = document.get("achievements", {})
    hint_source = document.get("hints", {})
    if not isinstance(meta_source, dict):
        raise ValueError("NELG+ meta must be an object.")
    if not isinstance(hint_source, dict):
        raise ValueError("NELG+ hints must be an object.")

    hints = {}
    for level_key, raw_level in hint_source.items():
        try:
            level = int(level_key)
        except (TypeError, ValueError) as error:
            raise ValueError(f"Hint level '{level_key}' is invalid.") from error
        if level <= 0 or level in hints:
            raise ValueError(f"Hint level {level} is invalid or duplicated.")
        if not isinstance(raw_level, dict):
            raise ValueError(f"Hint level {level} must be an object.")
        level_title = raw_level.get("title", f"Level {level}")
        if not isinstance(level_title, str) or not level_title.strip() or len(level_title) > 200:
            raise ValueError(f"Hint level {level} has an invalid title.")
        raw_hints = raw_level.get("hints")
        if not isinstance(raw_hints, list) or not 1 <= len(raw_hints) <= 25:
            raise ValueError(f"Hint level {level} needs 1 to 25 hints.")
        entries = []
        for number, raw_hint in enumerate(raw_hints, start=1):
            if not isinstance(raw_hint, dict):
                raise ValueError(f"Level {level} hint {number} must be an object.")
            title = raw_hint.get("title")
            body = raw_hint.get("text")
            if not isinstance(title, str) or not title.strip() or len(title) > 100:
                raise ValueError(f"Level {level} hint {number} has an invalid title.")
            if not isinstance(body, str) or not body.strip() or len(body) > 1024:
                raise ValueError(f"Level {level} hint {number} has invalid text.")
            entries.append({"title": title.strip(), "text": body.strip()})
        hints[level] = {
            "title": level_title.strip(),
            "hints": entries,
        }

    achievements = []
    used_ids = set()
    used_codes = set()
    code_lookup = {}
    for key, raw_item in _catalog_items(source):
        if not isinstance(raw_item, dict):
            raise ValueError(f"Achievement '{key}' must be an object.")
        try:
            achievement_id = int(raw_item.get("id", key))
        except (TypeError, ValueError) as error:
            raise ValueError(f"Achievement '{key}' has an invalid ID.") from error
        if achievement_id <= 0 or achievement_id in used_ids:
            raise ValueError(f"Achievement ID {achievement_id} is invalid or duplicated.")

        codes = _read_codes(raw_item)
        if not codes:
            raise ValueError(f"Achievement {achievement_id} has an empty code.")
        normalized_codes = [code.casefold() for code in codes]
        duplicates = used_codes.intersection(normalized_codes)
        if duplicates:
            raise ValueError(f"Achievement {achievement_id} has a duplicated code.")

        used_ids.add(achievement_id)
        used_codes.update(normalized_codes)
        achievement = {
            "id": achievement_id,
            "code": codes[0],
            "codes": codes,
            "title": str(
                raw_item.get("title", raw_item.get("name", f"Achievement {achievement_id}"))
            ),
            "description": str(
                raw_item.get("description", raw_item.get("condition", ""))
            ),
            "hidden": bool(raw_item.get("hidden", raw_item.get("secret", False))),
            "xp": max(0, int(raw_item.get("xp", 0))),
            "money": max(0, int(raw_item.get("money", 0))),
            "skin": (
                int(raw_item["skin"])
                if raw_item.get("skin") not in (None, "")
                else None
            ),
        }
        achievements.append(achievement)
        for normalized_code in normalized_codes:
            code_lookup[normalized_code] = achievement

    achievements.sort(key=lambda item: item["id"])
    meta = {
        "title": str(meta_source.get("title", "NELG Plus")),
        "release": str(meta_source.get("release", "In development")),
        "color": _normalize_color(meta_source.get("color", "#A8E6CF")),
    }
    return {
        "meta": meta,
        "achievements": achievements,
        "codes": code_lookup,
        "hints": dict(sorted(hints.items())),
    }
