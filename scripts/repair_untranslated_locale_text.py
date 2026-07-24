from __future__ import annotations

import json
import re
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from config.settings import get_required_env  # noqa: E402
from fcts.translator import DeepLTranslator  # noqa: E402


LOCALES_DIR = ROOT / "locales"
SOURCE_PATH = LOCALES_DIR / "ko.json"
TARGETS = {
    "en": "EN-US",
    "ja": "JA",
    "zh-CN": "ZH-HANS",
    "zh-TW": "ZH-HANT",
}
ALLOW_HANGUL_KEYS = {
    "cmd.03.t006",
    "cmd.03.t008",
}
HANGUL_PATTERN = re.compile(r"[\uac00-\ud7a3]")
PROTECTED_PATTERN = re.compile(
    r"(\{[A-Za-z_][^}]*\}|"
    r"<(?::[A-Za-z0-9_]+:\d+|@!?\d+|@&\d+|#\d+)>|"
    r"https?://[^\s]+)"
)


def protect_text(text: str) -> tuple[str, dict[str, str]]:
    protected: dict[str, str] = {}

    def replace(match: re.Match[str]) -> str:
        token = f"ZXQ{len(protected):04d}QXZ"
        protected[token] = match.group(0)
        return token

    return PROTECTED_PATTERN.sub(replace, text), protected


def restore_text(text: str, protected: dict[str, str]) -> str:
    restored = text
    for token, original in protected.items():
        restored = re.sub(
            re.escape(token),
            lambda _match, value=original: value,
            restored,
            flags=re.IGNORECASE,
        )
    return restored


def main() -> int:
    source = json.loads(SOURCE_PATH.read_text(encoding="utf-8"))
    translator = DeepLTranslator(get_required_env("DEEPL_API_KEY"))

    for language, target in TARGETS.items():
        path = LOCALES_DIR / f"{language}.json"
        locale = json.loads(path.read_text(encoding="utf-8"))
        keys = [
            key
            for key, value in locale.items()
            if key not in ALLOW_HANGUL_KEYS and HANGUL_PATTERN.search(value)
        ]
        if not keys:
            print(f"{language}: no untranslated text")
            continue

        prepared = [protect_text(source[key]) for key in keys]
        results = translator.translate_many(
            "KO",
            target,
            [text for text, _tokens in prepared],
        )

        for key, result, (_text, tokens) in zip(keys, results, prepared):
            locale[key] = restore_text(result["text"], tokens)

        path.write_text(
            json.dumps(locale, ensure_ascii=False, indent=2) + "\n",
            encoding="utf-8",
        )
        print(f"{language}: repaired {len(keys)} entries")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
