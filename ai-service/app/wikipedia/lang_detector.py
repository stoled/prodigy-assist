from langdetect import detect, LangDetectException

SUPPORTED_LANGS = {"ru", "en"}
DEFAULT_LANG = "en"


def detect_lang(text: str) -> str:
    """
    Detects the language of the text.
    Returns "ru" or "en". For any other language — "en".
    """
    try:
        lang = detect(text)
        return lang if lang in SUPPORTED_LANGS else DEFAULT_LANG
    except LangDetectException:
        return DEFAULT_LANG
