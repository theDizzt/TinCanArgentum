"""Read administrator credentials without caching or logging their contents."""

import json

from project_paths import CONFIG_DIR


ADMIN_CONFIG_PATH = CONFIG_DIR / "admin.json"


class AdminConfigError(ValueError):
    """The administrator configuration has an invalid structure."""


def load_admins():
    # utf-8-sig also accepts ordinary UTF-8 and files saved with a Windows BOM.
    with ADMIN_CONFIG_PATH.open(encoding="utf-8-sig") as file:
        admins = json.load(file)
    if not isinstance(admins, dict):
        raise AdminConfigError("Expected a JSON object")
    for user, credentials in admins.items():
        if not user.startswith("UID") or not user[3:].isascii() or not user[3:].isdigit():
            raise AdminConfigError("Expected UID followed by a Discord user ID")
        if not isinstance(credentials, dict) or any(
            not isinstance(credentials.get(field), str) or not credentials[field]
            for field in ("id", "pw")
        ):
            raise AdminConfigError("Admin id and pw must be nonempty strings")
    return admins
