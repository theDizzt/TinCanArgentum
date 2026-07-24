import json
from pathlib import Path
import discord
from discord import app_commands

BASE_DIR = Path(__file__).resolve().parent.parent
LOCALES_DIR = BASE_DIR / "locales"

def load_locale_file(lang: str) -> dict:
    path = LOCALES_DIR / f"{lang}.json"
    if not path.exists():
        return {}

    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)

class JsonTranslator(app_commands.Translator):
    def __init__(self):
        self.translations = {
            "ko": load_locale_file("ko"),
            "en-US": load_locale_file("en"),
            "en-GB": load_locale_file("en"),
            "ja": load_locale_file("ja"),
            "zh-CN": load_locale_file("zh-CN"),
            "zh-TW": load_locale_file("zh-TW"),
        }

        self.fallback = load_locale_file("ko")

    async def translate(
        self,
        string: app_commands.locale_str,
        locale: discord.Locale,
        context: app_commands.TranslationContext
    ) -> str | None:
        key = string.extras.get("key", string.message)
        locale_code = str(locale)

        lang_table = self.translations.get(locale_code, self.fallback)
        return lang_table.get(key, self.fallback.get(key, key))
