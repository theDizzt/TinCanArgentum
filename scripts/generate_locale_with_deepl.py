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
BATCH_SIZE = 40

TARGETS = {
    "ja": "JA",
    "zh-CN": "ZH-HANS",
    "zh-TW": "ZH-HANT",
}

COMMAND_NAME_OVERRIDES = {
    "ja": {
        "cmd.02.name": "私のid",
        "cmd.07.name": "アルゲンタムボット",
        "cmd.08.name": "ピング",
        "cmd.12.name": "エンブレム",
        "cmd.17.name": "装備",
        "cmd.30.name": "今日の主役",
        "cmd.36.name": "怒号",
        "cmd.37.name": "tod指数",
        "cmd.47.name": "ポケマンテル",
        "cmd.61.name": "入室",
        "cmd.82.name": "わざマシン再読込",
        "cmd.83.name": "図鑑再読込",
        "cmd.85.name": "わざマシン",
        "cmd.98.name": "カカオトーク",
    },
    "zh-CN": {
        "cmd.02.name": "我的id",
        "cmd.07.name": "argentum机器人",
        "cmd.08.name": "延迟",
        "cmd.10.name": "kakaodata",
        "cmd.12.name": "徽章",
        "cmd.17.name": "装备",
        "cmd.30.name": "今日主角",
        "cmd.34.name": "恩比词典",
        "cmd.36.name": "怒吼",
        "cmd.37.name": "tod指数",
        "cmd.47.name": "宝可梦猜谜",
        "cmd.61.name": "加入",
        "cmd.82.name": "技能机重载",
        "cmd.83.name": "图鉴重载",
        "cmd.85.name": "技能机",
        "cmd.98.name": "kakaotalk",
    },
    "zh-TW": {
        "cmd.07.name": "argentum機器人",
        "cmd.08.name": "延遲",
        "cmd.10.name": "kakaodata",
        "cmd.12.name": "徽章",
        "cmd.17.name": "裝備",
        "cmd.30.name": "今日主角",
        "cmd.34.name": "銀比辭典",
        "cmd.36.name": "怒吼",
        "cmd.37.name": "tod指數",
        "cmd.47.name": "寶可夢猜謎",
        "cmd.61.name": "加入",
        "cmd.82.name": "技能機重載",
        "cmd.83.name": "圖鑑重載",
        "cmd.85.name": "技能機",
        "cmd.98.name": "kakaotalk",
    },
}

TEXT_OVERRIDES = {
    "ja": {
        "cmd.36.prompt": "叫びたい文章を入力してください。例：`?rage 本当に腹が立つ！`",
        "cmd.39.too_long": "翻訳する文章は{max_length}文字以内で入力してください。",
        "cmd.39.not_configured": "DeepL APIキーが設定されていません。`.env`の`DEEPL_API_KEY`を確認してください。",
    },
    "zh-CN": {
        "cmd.36.prompt": "请输入要喊出的内容。例如：`?rage 我真的很生气！`",
        "cmd.39.too_long": "待翻译的文本不能超过{max_length}个字符。",
        "cmd.39.not_configured": "尚未设置DeepL API密钥。请检查`.env`中的`DEEPL_API_KEY`。",
    },
    "zh-TW": {
        "cmd.36.prompt": "請輸入要喊出的內容。例如：`?rage 我真的很生氣！`",
        "cmd.39.too_long": "待翻譯的文字不能超過{max_length}個字元。",
        "cmd.39.not_configured": "尚未設定DeepL API金鑰。請檢查`.env`中的`DEEPL_API_KEY`。",
    },
}

PROTECTED_PATTERN = re.compile(
    r"(\{[A-Za-z_][^}]*\}|"
    r"<(?::[A-Za-z0-9_]+:\d+|@!?\d+|@&\d+|#\d+)>|"
    r"https?://[^\s]+|"
    r"`[^`\n]*`)"
)
PLACEHOLDER_PATTERN = re.compile(r"\{[A-Za-z_][^}]*\}")


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

    missing = [token for token in protected if token.lower() in restored.lower()]
    if missing:
        raise RuntimeError(f"Failed to restore protected tokens: {missing}")
    return restored


def translate_locale(
    translator: DeepLTranslator,
    source: dict[str, str],
    target_code: str,
    language: str,
) -> dict[str, str]:
    keys = list(source)
    prepared = [protect_text(source[key]) for key in keys]
    translated_values: list[str] = []

    for start in range(0, len(prepared), BATCH_SIZE):
        batch = prepared[start:start + BATCH_SIZE]
        results = translator.translate_many(
            "KO",
            target_code,
            [text for text, _tokens in batch],
        )
        translated_values.extend(result["text"] for result in results)
        print(
            f"  translated {min(start + BATCH_SIZE, len(prepared))}"
            f"/{len(prepared)}",
            flush=True,
        )

    translated: dict[str, str] = {}
    for key, value, (_text, tokens) in zip(keys, translated_values, prepared):
        restored = restore_text(value, tokens)
        if key.endswith(".name"):
            restored = re.sub(r"\s+", "", restored)
        translated[key] = restored

        if set(PLACEHOLDER_PATTERN.findall(source[key])) != set(
            PLACEHOLDER_PATTERN.findall(restored)
        ):
            raise RuntimeError(f"Placeholder mismatch after translating {key}")

    translated.update(COMMAND_NAME_OVERRIDES.get(language, {}))
    translated.update(TEXT_OVERRIDES.get(language, {}))
    return translated


def main() -> int:
    selected = sys.argv[1:] or list(TARGETS)
    unknown = [language for language in selected if language not in TARGETS]
    if unknown:
        print(f"Unknown locale(s): {', '.join(unknown)}")
        return 2

    with SOURCE_PATH.open("r", encoding="utf-8") as file:
        source = json.load(file)

    translator = DeepLTranslator(get_required_env("DEEPL_API_KEY"))
    generated: dict[Path, dict[str, str]] = {}

    for language in selected:
        print(f"Generating {language}...", flush=True)
        generated[LOCALES_DIR / f"{language}.json"] = translate_locale(
            translator,
            source,
            TARGETS[language],
            language,
        )

    for path, data in generated.items():
        path.write_text(
            json.dumps(data, ensure_ascii=False, indent=2) + "\n",
            encoding="utf-8",
        )
        print(f"Wrote {path}", flush=True)

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
