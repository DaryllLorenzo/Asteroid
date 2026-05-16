import json
from pathlib import Path

_translations: dict[str, str] = {}
_current_lang: str = "en"


def load_language(lang: str) -> None:
    global _translations, _current_lang
    _current_lang = lang
    file_path = Path(__file__).parent / f"{lang}.json"
    if file_path.exists():
        with open(file_path, encoding="utf-8") as f:
            _translations = json.load(f)
    else:
        _translations = {}


def get_language() -> str:
    return _current_lang


def tr(text: str) -> str:
    return _translations.get(text, text)
