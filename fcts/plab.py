"""Persistence helpers for the PLab feature (command ID 29)."""

import json
import sqlite3
from contextlib import closing
from datetime import datetime
import re

from project_paths import CONFIG_DIR, DATA_DIR


DB_PATH = DATA_DIR / "plab.db"
CATALOG_PATH = CONFIG_DIR / "plab.json"
TABLE_NAME = "users"
FLAG_COUNT = 1024
DATE_PATTERN = re.compile(r"^\d{4}-\d{2}-\d{2}$")


def _flag_column_definition(flag_id: int) -> str:
    column = f"id{flag_id}"
    return (
        f"{column} INTEGER NOT NULL DEFAULT 0 "
        f"CHECK ({column} IN (0, 1))"
    )


def initSetting() -> None:
    """Create ``data/plab.db`` and its user table when they do not exist."""
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    flag_columns = ",\n        ".join(
        _flag_column_definition(flag_id)
        for flag_id in range(1, FLAG_COUNT + 1)
    )
    create_sql = f"""
    CREATE TABLE IF NOT EXISTS {TABLE_NAME} (
        id INTEGER PRIMARY KEY,
        lab_point INTEGER NOT NULL DEFAULT 0,
        skill_level INTEGER NOT NULL DEFAULT 0,
        startdate TEXT NOT NULL DEFAULT (date('now', '+9 hours')),
        {flag_columns}
    );
    """

    with closing(sqlite3.connect(DB_PATH)) as connection:
        connection.execute(create_sql)
        connection.commit()


def registerUser(user_id: int) -> bool:
    """Add a user with all defaults; return whether a row was inserted."""
    with closing(sqlite3.connect(DB_PATH)) as connection:
        cursor = connection.execute(
            f"INSERT OR IGNORE INTO {TABLE_NAME} (id) VALUES (?)",
            (int(user_id),),
        )
        connection.commit()
        return cursor.rowcount == 1


def userExists(user_id: int) -> bool:
    """Return whether a PLab row exists for the selected user."""
    with closing(sqlite3.connect(DB_PATH)) as connection:
        cursor = connection.execute(
            f"SELECT 1 FROM {TABLE_NAME} WHERE id = ?",
            (int(user_id),),
        )
        return cursor.fetchone() is not None


def _update_user_value(user_id: int, sql: str, parameters: tuple) -> bool:
    """Execute an update and report whether the selected user existed."""
    with closing(sqlite3.connect(DB_PATH)) as connection:
        cursor = connection.execute(sql, (*parameters, int(user_id)))
        connection.commit()
        return cursor.rowcount == 1


def startDateModifyById(user_id: int, value: str) -> bool:
    """Replace a user's start date after strict YYYY-MM-DD validation."""
    date_value = str(value).strip()
    if not DATE_PATTERN.fullmatch(date_value):
        raise ValueError("The date must use YYYY-MM-DD format.")
    try:
        datetime.strptime(date_value, "%Y-%m-%d")
    except ValueError as error:
        raise ValueError("The date is not valid.") from error
    return _update_user_value(
        user_id,
        f"UPDATE {TABLE_NAME} SET startdate = ? WHERE id = ?",
        (date_value,),
    )


def labPointModifyById(user_id: int, value: int) -> bool:
    """Replace a user's laboratory point value."""
    return _update_user_value(
        user_id,
        f"UPDATE {TABLE_NAME} SET lab_point = ? WHERE id = ?",
        (int(value),),
    )


def labPointAddById(user_id: int, value: int) -> bool:
    """Add a signed integer to a user's laboratory points atomically."""
    return _update_user_value(
        user_id,
        f"UPDATE {TABLE_NAME} SET lab_point = lab_point + ? WHERE id = ?",
        (int(value),),
    )


def readUser(user_id: int):
    """Return the complete PLab row for future command implementations."""
    with closing(sqlite3.connect(DB_PATH)) as connection:
        cursor = connection.execute(
            f"SELECT * FROM {TABLE_NAME} WHERE id = ?",
            (int(user_id),),
        )
        return cursor.fetchone()


def getUserState(user_id: int) -> dict:
    """Return profile values and all 1,024 completion flags for a user."""
    normalized_id = int(user_id)
    row = readUser(normalized_id)
    if row is None:
        registerUser(normalized_id)
        row = readUser(normalized_id)
    return {
        "id": row[0],
        "lab_point": row[1],
        "skill_level": row[2],
        "startdate": row[3],
        "flags": {
            flag_id: int(row[flag_id + 3])
            for flag_id in range(1, FLAG_COUNT + 1)
        },
    }


def loadAchievements() -> list[dict]:
    """Load and normalize achievement definitions from config/plab.json."""
    with CATALOG_PATH.open(encoding="utf-8") as file:
        document = json.load(file)

    source = document.get("achievements", {})
    if not isinstance(source, dict):
        raise ValueError("'achievements' must be a JSON object.")

    achievements = []
    used_ids = set()
    for key, raw_item in source.items():
        if not isinstance(raw_item, dict):
            raise ValueError(f"Achievement '{key}' must be a JSON object.")
        try:
            fallback_id = str(key).removeprefix("id")
            achievement_id = int(raw_item.get("id", fallback_id))
        except (TypeError, ValueError) as error:
            raise ValueError(f"Achievement '{key}' has an invalid ID.") from error
        if not 1 <= achievement_id <= FLAG_COUNT:
            raise ValueError(
                f"Achievement ID {achievement_id} must be between 1 and {FLAG_COUNT}."
            )
        if achievement_id in used_ids:
            raise ValueError(f"Achievement ID {achievement_id} is duplicated.")
        used_ids.add(achievement_id)
        achievements.append({
            "id": achievement_id,
            "name": str(raw_item.get("name", f"Achievement {achievement_id}")),
            "description": str(raw_item.get("description", "")),
            "tier": int(raw_item.get("tier", 0)),
            "url": str(raw_item.get("url", "")).strip(),
        })

    achievements.sort(key=lambda item: item["id"])
    return achievements
