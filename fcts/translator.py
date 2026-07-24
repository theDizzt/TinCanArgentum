import json
import re
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen


DEEPL_FREE_URL = "https://api-free.deepl.com/v2/translate"
DEEPL_PRO_URL = "https://api.deepl.com/v2/translate"

SOURCE_LANGUAGE_ALIASES = {
    "en-gb": "EN",
    "en-us": "EN",
    "no": "NB",
    "pt-br": "PT",
    "pt-pt": "PT",
    "zh-cn": "ZH",
    "zh-hans": "ZH",
    "zh-hant": "ZH",
    "zh-tw": "ZH",
}

TARGET_LANGUAGE_ALIASES = {
    "en": "EN-US",
    "no": "NB",
    "pt": "PT-BR",
    "zh": "ZH-HANS",
    "zh-cn": "ZH-HANS",
    "zh-hans": "ZH-HANS",
    "zh-hant": "ZH-HANT",
    "zh-tw": "ZH-HANT",
}

LANGUAGE_CODE_PATTERN = re.compile(r"^[A-Z]{2,3}(?:-[A-Z0-9]{2,5})?$")


class DeepLTranslationError(Exception):
    def __init__(self, message, status_code=None):
        super().__init__(message)
        self.status_code = status_code


def normalize_language_code(language, *, target=False):
    code = str(language).strip().lower().replace("_", "-")

    if not target and code in {"", "auto", "detect"}:
        return None

    aliases = TARGET_LANGUAGE_ALIASES if target else SOURCE_LANGUAGE_ALIASES
    normalized = aliases.get(code, code.upper())
    if not LANGUAGE_CODE_PATTERN.fullmatch(normalized):
        raise ValueError(f"Invalid language code: {language}")
    return normalized


class DeepLTranslator:
    def __init__(self, api_key, timeout=20):
        self.api_key = api_key.strip()
        self.timeout = timeout
        self.baseurl = (
            DEEPL_FREE_URL if self.api_key.endswith(":fx") else DEEPL_PRO_URL
        )

    def translate(self, source_language, target_language, text):
        return self.translate_many(
            source_language,
            target_language,
            [text],
        )[0]

    def translate_many(self, source_language, target_language, texts):
        source = normalize_language_code(source_language)
        target = normalize_language_code(target_language, target=True)
        text_list = [str(text) for text in texts]
        if not text_list:
            raise ValueError("At least one text is required.")

        payload = {
            "text": text_list,
            "target_lang": target,
        }
        if source is not None:
            payload["source_lang"] = source

        request = Request(
            self.baseurl,
            data=json.dumps(payload, ensure_ascii=False).encode("utf-8"),
            headers={
                "Authorization": f"DeepL-Auth-Key {self.api_key}",
                "Content-Type": "application/json",
                "User-Agent": "TinCanArgentum/DeepL",
            },
            method="POST",
        )

        try:
            with urlopen(request, timeout=self.timeout) as response:
                result = json.load(response)
        except HTTPError as error:
            message = self._read_http_error(error)
            raise DeepLTranslationError(message, error.code) from error
        except URLError as error:
            raise DeepLTranslationError(f"Network error: {error.reason}") from error
        except (json.JSONDecodeError, UnicodeDecodeError) as error:
            raise DeepLTranslationError("DeepL returned an invalid response.") from error

        try:
            translations = [
                {
                    "text": translation["text"],
                    "detected_source_language": translation.get(
                        "detected_source_language"
                    ),
                }
                for translation in result["translations"]
            ]
            if len(translations) != len(text_list):
                raise DeepLTranslationError(
                    "DeepL returned an unexpected number of translations."
                )
            return translations
        except (KeyError, TypeError) as error:
            raise DeepLTranslationError(
                "DeepL response did not contain a translation."
            ) from error

    @staticmethod
    def _read_http_error(error):
        try:
            result = json.loads(error.read().decode("utf-8"))
            return result.get("message", str(error))
        except (json.JSONDecodeError, UnicodeDecodeError, AttributeError):
            return str(error)
