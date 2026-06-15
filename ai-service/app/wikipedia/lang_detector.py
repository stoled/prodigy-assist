from langdetect import detect, LangDetectException

SUPPORTED_LANGS = {"ru", "en"}
DEFAULT_LANG = "en"


def detect_lang(text: str) -> str:
    """
    Определяет язык текста.
    Возвращает "ru" или "en". Для всех остальных языков — "en".
    """
    try:
        lang = detect(text)
        return lang if lang in SUPPORTED_LANGS else DEFAULT_LANG
    except LangDetectException:
        return DEFAULT_LANG
