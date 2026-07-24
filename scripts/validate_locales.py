from __future__ import annotations

import json
import re
import sys
from collections import Counter
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
LOCALES_DIR = ROOT / "locales"
SOURCE_DIRS = (ROOT / "cogs", ROOT / "fcts", ROOT / "games")
SOURCE_FILES = (ROOT / "main.py",)
PLANNED_COMMAND_IDS = {78, 88}

ID_PATTERN = re.compile(r"\[\s*id\s*:\s*(\d+)", re.IGNORECASE)
KEY_PATTERN = re.compile(r"^(cmd\.\d{2}\.(?:name|desc)|.+)$")
PLACEHOLDER_PATTERN = re.compile(r"\{([A-Za-z_][A-Za-z0-9_]*)(?:[^}]*)\}")
RUNTIME_KEY_PATTERN = re.compile(
    r"""i18n\.t\(\s*[^,]+,\s*["']([^"']+)["']""",
    re.MULTILINE,
)
DECORATOR_KEY_PATTERN = re.compile(
    r"""locale_str\(\s*["'][^"']*["']\s*,\s*key\s*=\s*["']([^"']+)["']""",
    re.MULTILINE,
)
ENGLISH_COMMAND_NAME_PATTERN = re.compile(r"^[a-z0-9_-]+$")
HANGUL_PATTERN = re.compile(r"[\uac00-\ud7a3]")
ALLOWED_FOREIGN_HANGUL_KEYS = {
    "cmd.03.t006",
    "cmd.03.t008",
}


class DuplicateKeyError(ValueError):
    pass


def unique_object(pairs: list[tuple[str, Any]]) -> dict[str, Any]:
    counts = Counter(key for key, _ in pairs)
    duplicates = sorted(key for key, count in counts.items() if count > 1)
    if duplicates:
        raise DuplicateKeyError(f"duplicate keys: {', '.join(duplicates)}")
    return dict(pairs)


def load_locale(path: Path) -> dict[str, str]:
    with path.open("r", encoding="utf-8") as file:
        data = json.load(file, object_pairs_hook=unique_object)

    if not isinstance(data, dict):
        raise ValueError("locale root must be a JSON object")
    if any(not isinstance(key, str) or not isinstance(value, str) for key, value in data.items()):
        raise ValueError("all locale keys and values must be strings")
    return data


def iter_source_files() -> list[Path]:
    files = list(SOURCE_FILES)
    for directory in SOURCE_DIRS:
        files.extend(
            path
            for path in directory.rglob("*.py")
            if "backup" not in path.parts and "__pycache__" not in path.parts
        )
    return files


def collect_source() -> str:
    return "\n".join(path.read_text(encoding="utf-8") for path in iter_source_files())


def command_ids(source: str) -> set[int]:
    return {int(value) for value in ID_PATTERN.findall(source)} | PLANNED_COMMAND_IDS


def placeholders(value: str) -> set[str]:
    return set(PLACEHOLDER_PATTERN.findall(value))


def validate() -> list[str]:
    errors: list[str] = []
    locale_paths = sorted(LOCALES_DIR.glob("*.json"))
    if not locale_paths:
        return ["no locale JSON files found"]

    locales: dict[str, dict[str, str]] = {}
    for path in locale_paths:
        try:
            locales[path.stem] = load_locale(path)
        except (OSError, json.JSONDecodeError, ValueError) as error:
            errors.append(f"{path.name}: {error}")

    if "ko" not in locales:
        errors.append("ko.json is required as the fallback locale")
        return errors

    base = locales["ko"]
    base_keys = set(base)
    source = collect_source()
    ids = command_ids(source)

    for lang, table in locales.items():
        keys = set(table)
        missing = sorted(base_keys - keys)
        extra = sorted(keys - base_keys)
        if missing:
            errors.append(f"{lang}: missing keys: {', '.join(missing)}")
        if extra:
            errors.append(f"{lang}: extra keys: {', '.join(extra)}")

        for command_id in sorted(ids):
            prefix = f"cmd.{command_id:02d}"
            for suffix in ("name", "desc"):
                key = f"{prefix}.{suffix}"
                value = table.get(key, "")
                if not value.strip():
                    errors.append(f"{lang}: missing or empty {key}")

            name = table.get(f"{prefix}.name", "")
            description = table.get(f"{prefix}.desc", "")
            if len(name) > 32:
                errors.append(f"{lang}: {prefix}.name exceeds 32 characters")
            if len(description) > 100:
                errors.append(f"{lang}: {prefix}.desc exceeds 100 characters")
            if any(character.isspace() for character in name):
                errors.append(f"{lang}: {prefix}.name contains whitespace")
            if name != name.lower():
                errors.append(
                    f"{lang}: {prefix}.name contains uppercase characters: {name}"
                )
            invalid_characters = sorted({
                character
                for character in name
                if not (character.isalnum() or character in "-_")
            })
            if invalid_characters:
                errors.append(
                    f"{lang}: {prefix}.name contains invalid characters: "
                    f"{''.join(invalid_characters)}"
                )
            if lang == "en" and name and not ENGLISH_COMMAND_NAME_PATTERN.fullmatch(name):
                errors.append(f"{lang}: {prefix}.name has invalid characters: {name}")

        for key in sorted(base_keys & keys):
            if placeholders(base[key]) != placeholders(table[key]):
                errors.append(
                    f"{lang}: placeholder mismatch for {key}: "
                    f"ko={sorted(placeholders(base[key]))}, "
                    f"{lang}={sorted(placeholders(table[key]))}"
                )
            if (
                lang != "ko"
                and key not in ALLOWED_FOREIGN_HANGUL_KEYS
                and HANGUL_PATTERN.search(table[key])
            ):
                errors.append(f"{lang}: untranslated Hangul remains in {key}")

    referenced_keys = set(RUNTIME_KEY_PATTERN.findall(source))
    referenced_keys.update(DECORATOR_KEY_PATTERN.findall(source))
    missing_references = sorted(referenced_keys - base_keys)
    if missing_references:
        errors.append(f"source references missing locale keys: {', '.join(missing_references)}")

    return errors


def main() -> int:
    errors = validate()
    if errors:
        print("Locale validation failed:")
        for error in errors:
            print(f"- {error}")
        return 1

    locale_count = len(list(LOCALES_DIR.glob("*.json")))
    print(f"Locale validation passed ({locale_count} locales).")
    return 0


if __name__ == "__main__":
    sys.exit(main())
