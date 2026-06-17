import logging
from datetime import datetime

from mcp.server.fastmcp import FastMCP

from app.services.rag_service import search, format_context, save_document, index_document
from app.wikipedia.fetcher import fetch_wikipedia
from app.wikipedia.parser import article_to_text

logger = logging.getLogger(__name__)

mcp = FastMCP("prodigy-mcp")


@mcp.tool()
async def search_knowledge(query: str, top_k: int = 5) -> str:
    """Поиск по базе знаний. Возвращает релевантные фрагменты с источниками."""
    chunks = await search(query=query, top_k=top_k, min_score=0.5)
    if not chunks:
        return "Ничего не найдено."

    context = format_context(chunks)
    return context


@mcp.tool()
async def fetch_wikipedia_article(topic: str, lang: str = "en") -> str:
    """Загрузка статьи из Wikipedia по теме. Возвращает текст статьи."""
    article = await fetch_wikipedia(topic, lang=lang)
    if not article:
        return f"Статья по теме '{topic}' не найдена."

    text = article_to_text(article)
    return f"Title: {article.title}\nURL: {article.url}\n\n{text[:3000]}"


@mcp.tool()
async def save_knowledge(title: str, content: str, source: str, lang: str = "en") -> str:
    """Сохранить новый документ в базу знаний и проиндексировать его."""
    document_id = await save_document(
        title=title,
        content=content,
        source=source,
        lang=lang,
    )
    chunks_count = await index_document(document_id, content)
    return f"Документ '{title}' сохранён (ID: {document_id}). Индексировано {chunks_count} чанков."


@mcp.tool()
def get_current_time() -> str:
    """Возвращает текущее время и дату."""
    now = datetime.now()
    return now.strftime("%Y-%m-%d %H:%M:%S")


@mcp.tool()
async def generate_image(prompt: str) -> str:
    """Генерация изображения по описанию (заглушка)."""
    logger.info("Image generation requested (stub)", extra={"prompt": prompt})
    return (
        f"[Заглушка] Генерация изображения по запросу: '{prompt}'. "
        f"Функция будет доступна в Итерации 6 (DALL-E + MinIO)."
    )
