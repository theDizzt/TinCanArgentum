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

# Ranks 12-14 also require the listed skill level.  When that requirement is
# not met, the user remains at rank 11 even if they have enough LAB points.
PLAB_RANK_REQUIREMENTS = (
    (14, 10000, 10),
    (13, 6000, 9),
    (12, 4000, 9),
    (11, 3000, 0),
    (10, 2200, 0),
    (9, 1500, 0),
    (8, 1000, 0),
    (7, 600, 0),
    (6, 450, 0),
    (5, 320, 0),
    (4, 210, 0),
    (3, 120, 0),
    (2, 50, 0),
    (1, 1, 0),
)


def _flag_column_definition(flag_id: int) -> str:
    column = f"id{flag_id}"
    return (
        f"{column} INTEGER NOT NULL DEFAULT 0 "
        f"CHECK ({column} IN (0, 1))"
    )


def initSetting() -> None:
    """Create the PLab user and server speedrun tables when absent."""
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
        connection.execute(
            """
            CREATE TABLE IF NOT EXISTS clears (
                guild_id INTEGER NOT NULL,
                game_id INTEGER NOT NULL,
                user_id INTEGER NOT NULL,
                cleared_at TEXT NOT NULL DEFAULT
                    (datetime('now', '+9 hours')),
                PRIMARY KEY (guild_id, game_id, user_id)
            )
            """
        )
        connection.execute(
            """
            CREATE TABLE IF NOT EXISTS first_clears (
                guild_id INTEGER NOT NULL,
                game_id INTEGER NOT NULL,
                user_id INTEGER NOT NULL,
                assigned_at TEXT NOT NULL DEFAULT
                    (datetime('now', '+9 hours')),
                PRIMARY KEY (guild_id, game_id)
            )
            """
        )
        connection.execute(
            """
            CREATE INDEX IF NOT EXISTS idx_plab_clears_fastest
            ON clears (guild_id, game_id, cleared_at, user_id)
            """
        )
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


def getPlabRank(lab_point: int, skill_level: int) -> int:
    """Calculate the numeric PLab rank (0-14) from LAB and skill levels."""
    points = int(lab_point)
    skill = int(skill_level)
    for rank, required_points, required_skill in PLAB_RANK_REQUIREMENTS:
        if points >= required_points and skill >= required_skill:
            return rank
    return 0


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


def _normalize_game_id(game_id: int) -> int:
    normalized_id = int(game_id)
    if not 1 <= normalized_id <= FLAG_COUNT:
        raise ValueError(f"Game ID must be between 1 and {FLAG_COUNT}.")
    return normalized_id


def _repair_first_clear(connection, guild_id: int, game_id: int) -> int | None:
    """Assign the earliest recorded clear when the first slot is empty."""
    current = connection.execute(
        """
        SELECT first_clears.user_id
        FROM first_clears
        INNER JOIN clears
          ON clears.guild_id = first_clears.guild_id
         AND clears.game_id = first_clears.game_id
         AND clears.user_id = first_clears.user_id
        WHERE first_clears.guild_id = ? AND first_clears.game_id = ?
        """,
        (int(guild_id), int(game_id)),
    ).fetchone()
    if current is not None:
        return int(current[0])

    connection.execute(
        "DELETE FROM first_clears WHERE guild_id = ? AND game_id = ?",
        (int(guild_id), int(game_id)),
    )
    earliest = connection.execute(
        """
        SELECT user_id FROM clears
        WHERE guild_id = ? AND game_id = ?
        ORDER BY cleared_at ASC, user_id ASC
        LIMIT 1
        """,
        (int(guild_id), int(game_id)),
    ).fetchone()
    if earliest is None:
        return None

    first_user_id = int(earliest[0])
    connection.execute(
        """
        INSERT INTO first_clears (guild_id, game_id, user_id)
        VALUES (?, ?, ?)
        """,
        (int(guild_id), int(game_id), first_user_id),
    )
    return first_user_id


def setGameCompletion(
    user_id: int,
    game_id: int,
    completed: bool,
    guild_id: int,
) -> int | None:
    """Set completion and maintain the server's automatic first clear."""
    normalized_user_id = int(user_id)
    normalized_game_id = _normalize_game_id(game_id)
    normalized_guild_id = int(guild_id)
    column = f"id{normalized_game_id}"

    with closing(sqlite3.connect(DB_PATH)) as connection:
        connection.execute(
            f"INSERT OR IGNORE INTO {TABLE_NAME} (id) VALUES (?)",
            (normalized_user_id,),
        )
        connection.execute(
            f"UPDATE {TABLE_NAME} SET {column} = ? WHERE id = ?",
            (int(bool(completed)), normalized_user_id),
        )

        if completed:
            connection.execute(
                """
                INSERT OR IGNORE INTO clears (guild_id, game_id, user_id)
                VALUES (?, ?, ?)
                """,
                (normalized_guild_id, normalized_game_id, normalized_user_id),
            )
            first_user_id = _repair_first_clear(
                connection, normalized_guild_id, normalized_game_id
            )
        else:
            # Completion is global, so locking removes this clear from every
            # server and promotes the next recorded clearer where necessary.
            guild_rows = connection.execute(
                """
                SELECT DISTINCT guild_id FROM clears
                WHERE game_id = ? AND user_id = ?
                """,
                (normalized_game_id, normalized_user_id),
            ).fetchall()
            connection.execute(
                "DELETE FROM clears WHERE game_id = ? AND user_id = ?",
                (normalized_game_id, normalized_user_id),
            )
            connection.execute(
                "DELETE FROM first_clears WHERE game_id = ? AND user_id = ?",
                (normalized_game_id, normalized_user_id),
            )
            first_user_id = None
            for (affected_guild_id,) in guild_rows:
                repaired = _repair_first_clear(
                    connection, int(affected_guild_id), normalized_game_id
                )
                if int(affected_guild_id) == normalized_guild_id:
                    first_user_id = repaired
        connection.commit()

    recalculateAll()
    return first_user_id


def setFirstClear(user_id: int, game_id: int, guild_id: int) -> None:
    """Manually replace a server's first clearer for a completed game."""
    normalized_user_id = int(user_id)
    normalized_game_id = _normalize_game_id(game_id)
    normalized_guild_id = int(guild_id)
    column = f"id{normalized_game_id}"

    with closing(sqlite3.connect(DB_PATH)) as connection:
        completed = connection.execute(
            f"SELECT {column} FROM {TABLE_NAME} WHERE id = ?",
            (normalized_user_id,),
        ).fetchone()
        if completed is None or int(completed[0]) != 1:
            raise ValueError("The selected user has not completed that game.")

        connection.execute(
            """
            INSERT OR IGNORE INTO clears (guild_id, game_id, user_id)
            VALUES (?, ?, ?)
            """,
            (normalized_guild_id, normalized_game_id, normalized_user_id),
        )
        connection.execute(
            """
            INSERT INTO first_clears (guild_id, game_id, user_id)
            VALUES (?, ?, ?)
            ON CONFLICT(guild_id, game_id) DO UPDATE SET
                user_id = excluded.user_id,
                assigned_at = datetime('now', '+9 hours')
            """,
            (normalized_guild_id, normalized_game_id, normalized_user_id),
        )
        connection.commit()

    recalculateAll()


def recalculateAll() -> int:
    """Rebuild all LAB points and skill levels from canonical game data."""
    game_tiers = {
        item["id"]: max(0, int(item["tier"]))
        for item in loadAchievements()
    }
    with closing(sqlite3.connect(DB_PATH)) as connection:
        connection.execute(
            """
            DELETE FROM first_clears
            WHERE NOT EXISTS (
                SELECT 1 FROM clears
                WHERE clears.guild_id = first_clears.guild_id
                  AND clears.game_id = first_clears.game_id
                  AND clears.user_id = first_clears.user_id
            )
            """
        )
        clear_groups = connection.execute(
            "SELECT DISTINCT guild_id, game_id FROM clears"
        ).fetchall()
        for guild_id, game_id in clear_groups:
            _repair_first_clear(connection, int(guild_id), int(game_id))

        calculated = {}
        for row in connection.execute(f"SELECT * FROM {TABLE_NAME}").fetchall():
            user_id = int(row[0])
            completed_games = {
                game_id
                for game_id in game_tiers
                if int(row[game_id + 3]) == 1
            }
            calculated[user_id] = {
                "completed": completed_games,
                "lab_point": sum(
                    game_tiers[game_id] ** 2 for game_id in completed_games
                ),
                "skill_level": max(
                    (game_tiers[game_id] for game_id in completed_games),
                    default=0,
                ),
            }

        for game_id, user_id in connection.execute(
            "SELECT game_id, user_id FROM first_clears"
        ).fetchall():
            game_id = int(game_id)
            user_id = int(user_id)
            result = calculated.get(user_id)
            tier = game_tiers.get(game_id)
            if result is not None and tier is not None and game_id in result["completed"]:
                result["lab_point"] += 2 * (tier ** 2)

        connection.executemany(
            f"""
            UPDATE {TABLE_NAME}
            SET lab_point = ?, skill_level = ?
            WHERE id = ?
            """,
            (
                (result["lab_point"], result["skill_level"], user_id)
                for user_id, result in calculated.items()
            ),
        )
        connection.commit()
        return len(calculated)


def getRanking() -> list[dict]:
    """Return all PLab users ranked by LAB points, highest first."""
    with closing(sqlite3.connect(DB_PATH)) as connection:
        rows = connection.execute(
            f"""
            SELECT id, lab_point, skill_level,
                   RANK() OVER (ORDER BY lab_point DESC) AS ranking
            FROM {TABLE_NAME}
            ORDER BY lab_point DESC, id ASC
            """
        ).fetchall()
    return [
        {
            "id": int(row[0]),
            "lab_point": int(row[1]),
            "skill_level": int(row[2]),
            "ranking": int(row[3]),
        }
        for row in rows
    ]


def getUserRanking(user_id: int) -> int | None:
    """Return a user's LAB ranking, or None when no PLab row exists."""
    with closing(sqlite3.connect(DB_PATH)) as connection:
        row = connection.execute(
            f"""
            SELECT ranking FROM (
                SELECT id,
                       RANK() OVER (ORDER BY lab_point DESC) AS ranking
                FROM {TABLE_NAME}
            )
            WHERE id = ?
            """,
            (int(user_id),),
        ).fetchone()
    return int(row[0]) if row is not None else None
