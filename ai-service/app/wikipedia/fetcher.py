import wikipediaapi
from dataclasses import dataclass
from app.wikipedia.lang_detector import detect_lang


@dataclass
class WikipediaSection:
    title: str
    content: str


@dataclass
class WikipediaArticle:
    title: str
    url: str
    summary: str
    sections: list[WikipediaSection]
    lang: str


def _make_client(lang: str) -> wikipediaapi.Wikipedia:
    return wikipediaapi.Wikipedia(
        language=lang,
        user_agent="prodigy-knowledge-bot/1.0",
    )


async def fetch_wikipedia(topic: str, lang: str | None = None) -> WikipediaArticle | None:
    """
    Ищет и загружает статью из Wikipedia.
    Если lang не указан — определяет по тексту запроса.
    Возвращает None если статья не найдена.
    """
    if lang is None:
        lang = detect_lang(topic)

    client = _make_client(lang)
    page = client.page(topic)

    if not page.exists():
        # Fallback: попробовать на английском если не нашли на русском
        if lang == "ru":
            client = _make_client("en")
            page = client.page(topic)
            if not page.exists():
                return None
            lang = "en"
        else:
            return None

    sections = [
        WikipediaSection(title=s.title, content=s.text)
        for s in page.sections
        if s.text.strip()
    ]

    return WikipediaArticle(
        title=page.title,
        url=page.fullurl,
        summary=page.summary,
        sections=sections,
        lang=lang,
    )
