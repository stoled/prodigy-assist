import asyncio
import logging
from dataclasses import dataclass

import requests
import wikipediaapi
from app.wikipedia.lang_detector import detect_lang

logger = logging.getLogger(__name__)

WIKIPEDIA_API_ENDPOINTS = {
    "en": "https://en.wikipedia.org/w/api.php",
    "ru": "https://ru.wikipedia.org/w/api.php",
}

SEARCH_TIMEOUT = 5.0
SEARCH_LIMIT = 5
USER_AGENT = "Mozilla/5.0 (compatible; ProdigyBot/1.0; +https://github.com/stoled/prodigy-assist)"


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
        user_agent=USER_AGENT,
    )


def _mw_search_sync(query: str, lang: str = "en", limit: int = SEARCH_LIMIT) -> list[str]:
    endpoint = WIKIPEDIA_API_ENDPOINTS.get(lang, WIKIPEDIA_API_ENDPOINTS["en"])
    params = {
        "action": "query",
        "list": "search",
        "srsearch": query,
        "srlimit": limit,
        "srenablerewrites": 1,
        "format": "json",
        "utf8": 1,
    }
    headers = {"User-Agent": USER_AGENT}
    response = requests.get(endpoint, params=params, headers=headers, timeout=SEARCH_TIMEOUT)
    response.raise_for_status()
    data = response.json()
    return [item["title"] for item in data.get("query", {}).get("search", [])]


def _fetch_page_sync(lang: str, title: str) -> wikipediaapi.WikipediaPage:
    client = _make_client(lang)
    return client.page(title)


def extract_topic(query: str) -> str:
    stopwords = [
        "расскажи о", "расскажи про", "что такое", "кто такой", "кто такая",
        "что известно о", "что известно про", "объясни", "опиши",
        "tell me about", "what is", "who is", "explain", "describe",
        "what are", "how does", "how do",
    ]
    topic = query.strip().rstrip("?").strip()

    for stopword in stopwords:
        if topic.lower().startswith(stopword):
            topic = topic[len(stopword):].strip()
            break

    return topic


def _best_title(query: str, titles: list[str]) -> str | None:
    """
    Выбирает наиболее подходящий заголовок из результатов поиска.
    Предпочитает точное совпадение с запросом.
    """
    if not titles:
        return None

    query_lower = query.lower()

    # Точное совпадение
    for title in titles:
        if title.lower() == query_lower:
            return title

    # Частичное совпадение — заголовок содержит запрос
    for title in titles:
        if query_lower in title.lower():
            return title

    # Запрос содержит заголовок
    for title in titles:
        if title.lower() in query_lower:
            return title

    # Первый результат как fallback
    return titles[0]


async def _run_in_executor(func, *args):
    loop = asyncio.get_running_loop()
    return await loop.run_in_executor(None, lambda: func(*args))


async def search_titles(query: str, lang: str = "en", limit: int = SEARCH_LIMIT) -> list[str]:
    return await _run_in_executor(_mw_search_sync, query, lang, limit)


async def fetch_page(title: str, lang: str) -> wikipediaapi.WikipediaPage:
    return await _run_in_executor(_fetch_page_sync, lang, title)


async def fetch_wikipedia(topic: str, lang: str | None = None) -> WikipediaArticle | None:
    if lang is None:
        lang = detect_lang(topic)

    query = topic.strip()
    if not query:
        logger.debug("Empty Wikipedia query received")
        return None

    # Очищаем тему до поиска
    clean_query = extract_topic(query)
    logger.info("Searching Wikipedia", extra={"query": clean_query, "lang": lang})

    titles: list[str] = []
    try:
        titles = await asyncio.wait_for(
            search_titles(clean_query, lang), timeout=SEARCH_TIMEOUT + 1
        )
        logger.debug("Wikipedia search titles", extra={"titles": titles, "lang": lang})
    except Exception as exc:
        logger.warning("Wikipedia search failed", exc_info=exc)
        titles = []

    if not titles and lang == "ru":
        try:
            titles = await asyncio.wait_for(
                search_titles(clean_query, "en"), timeout=SEARCH_TIMEOUT + 1
            )
            if titles:
                logger.info("Wikipedia search fallback to English succeeded", extra={"titles": titles})
                lang = "en"
        except Exception as exc:
            logger.warning("Wikipedia search fallback failed", exc_info=exc)
            titles = []

    if not titles:
        logger.info("No Wikipedia titles found", extra={"query": clean_query, "lang": lang})
        return None

    best = _best_title(clean_query, titles)
    if not best:
        return None

    logger.debug("Best Wikipedia title selected", extra={"title": best, "lang": lang})

    try:
        page = await asyncio.wait_for(fetch_page(best, lang), timeout=SEARCH_TIMEOUT + 1)
        if not page or not page.exists():
            logger.info("Wikipedia page not found", extra={"title": best})
            return None

        sections = [
            WikipediaSection(title=s.title, content=s.text)
            for s in page.sections
            if s.text.strip()
        ]

        logger.info("Wikipedia article loaded", extra={"title": page.title, "url": page.fullurl})
        return WikipediaArticle(
            title=page.title,
            url=page.fullurl,
            summary=page.summary,
            sections=sections,
            lang=lang,
        )
    except Exception as exc:
        logger.warning("Failed to fetch Wikipedia page", exc_info=exc, extra={"title": best})
        return None
