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


def extract_topic(query: str) -> str:
    """
    Извлекает ключевую тему из вопроса в свободной форме.
    Убирает вопросительные слова и глаголы-вводные.
    """
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


async def fetch_wikipedia(topic: str, lang: str | None = None) -> WikipediaArticle | None:
    """
    Ищет и загружает статью из Wikipedia.
    Если lang не указан — определяет по тексту запроса.
    Возвращает None если статья не найдена.
    """
    if lang is None:
        lang = detect_lang(topic)

    # Извлекаем ключевую тему из вопроса
    clean_topic = extract_topic(topic)
    print(f"[Wikipedia] Clean topic: '{clean_topic}' (lang={lang})")

    client = _make_client(lang)
    page = client.page(clean_topic)

    if not page.exists():
        # Fallback: попробовать на английском если не нашли на русском
        if lang == "ru":
            client = _make_client("en")
            page = client.page(clean_topic)
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
