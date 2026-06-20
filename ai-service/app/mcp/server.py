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
    """Семантический поиск по базе знаний (статьи Wikipedia и сохранённые документы).
    Используй ВСЕГДА когда вопрос касается конкретного факта, человека, события,
    научного понятия или любой темы, требующей проверенной информации.
    НЕ используй для вопросов о текущем времени, дате или общих приветствий.
    Возвращает релевантные фрагменты текста с указанием источника (title + URL).
    """
    chunks = await search(query=query, top_k=top_k, min_score=0.5)
    if not chunks:
        return "Ничего не найдено в базе знаний."
    return format_context(chunks)


@mcp.tool()
async def fetch_wikipedia_article(topic: str, lang: str) -> str:
    """Загружает статью из Wikipedia по конкретной теме и индексирует её в базу знаний.
    Используй ТОЛЬКО если search_knowledge не нашёл достаточно информации.
    topic должен быть точным названием темы (например "Isaac Newton" или "Леонардо да Винчи"),
    а не полным вопросом пользователя.
    ВАЖНО: lang ОБЯЗАТЕЛЬНО должен совпадать с языком вопроса пользователя:
    "ru" если пользователь спросил на русском, "en" если на английском.
    Никогда не используй "ru" по умолчанию для англоязычных вопросов.
    """
    article = await fetch_wikipedia(topic, lang=lang)
    if not article:
        return f"Статья по теме '{topic}' не найдена в Wikipedia."
    text = article_to_text(article)
    return f"Title: {article.title}\nURL: {article.url}\n\n{text[:3000]}"


@mcp.tool()
async def save_knowledge(title: str, content: str, source: str, lang: str = "en") -> str:
    """Сохраняет произвольный текст в базу знаний для последующего поиска.
    Используй только если пользователь явно просит запомнить/сохранить информацию.
    """
    document_id = await save_document(title=title, content=content, source=source, lang=lang)
    chunks_count = await index_document(document_id, content)
    return f"Документ '{title}' сохранён (ID: {document_id}). Индексировано {chunks_count} чанков."


@mcp.tool()
def get_current_time() -> str:
    """Возвращает текущую дату и время сервера.
    Используй ВСЕГДА когда пользователь спрашивает который час, какая дата,
    какой сегодня день или год. НЕ используй search_knowledge для таких вопросов.
    """
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")


@mcp.tool()
async def generate_image(prompt: str) -> str:
    """Генерация изображения по текстовому описанию (заглушка, доступно в Итерации 6).
    Используй когда пользователь явно просит нарисовать или сгенерировать картинку.
    """
    logger.info("Image generation requested (stub)", extra={"prompt": prompt})
    return f"[Заглушка] Генерация изображения: '{prompt}'. Будет доступно в Итерации 6."


def create_sse_app():
    """Создаёт ASGI-приложение MCP Server с SSE транспортом."""
    return mcp.sse_app()
