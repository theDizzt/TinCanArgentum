import json
from pathlib import Path
import fcts.sqlcontrol as q

BASE_DIR = Path(__file__).resolve().parent.parent
LOCALES_DIR = BASE_DIR / "locales"

_locale_cache = {}

def load_locale(lang: str) -> dict:
    if lang in _locale_cache:
        return _locale_cache[lang]

    path = LOCALES_DIR / f"{lang}.json"
    if not path.exists():
        print(f"[I18N] locale '{lang}' not found, fallback to ko")
        path = LOCALES_DIR / "ko.json"

    with open(path, "r", encoding="utf-8") as f:
        data = json.load(f)

    _locale_cache[lang] = data
    return data

def get_user_lang(user) -> str:
    try:
        # readLanguage 함수 형태에 따라 둘 중 하나로 맞춰야 함
        lang = q.readLanguage(user)   # 또는 q.readLanguage(user.id)
        #print(f"[I18N] user={user} lang={lang}")
        if lang:
            return lang
    except Exception as e:
        # print(f"[I18N ERROR] get_user_lang failed: {e}")
        pass
    return "ko"

def t_by_lang(lang: str, key: str, **kwargs) -> str:
    data = load_locale(lang)
    fallback = load_locale("ko") if lang != "ko" else data

    text = data.get(key, fallback.get(key, key))
    return text.format(**kwargs)

def t(user, key: str, **kwargs) -> str:
    lang = get_user_lang(user)
    return t_by_lang(lang, key, **kwargs)