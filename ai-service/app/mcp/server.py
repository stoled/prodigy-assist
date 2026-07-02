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
    """Semantic search over the knowledge base (Wikipedia articles and saved documents).
    Use ALWAYS when the question concerns a specific fact, person, event,
    scientific concept or any topic requiring verified information.
    Do NOT use it for questions about the current time, date or general greetings.
    Returns relevant text chunks with the source (title + URL).
    """
    chunks = await search(query=query, top_k=top_k, min_score=0.5)
    if not chunks:
        return "Ничего не найдено в базе знаний."
    return format_context(chunks)


@mcp.tool()
async def fetch_wikipedia_article(topic: str, lang: str) -> str:
    """Fetches a Wikipedia article on a specific topic and indexes it into the knowledge base.
    Use ONLY if search_knowledge did not find enough information.
    topic must be the exact name of the topic (e.g. "Isaac Newton" or "Leonardo da Vinci"),
    not the user's full question.
    IMPORTANT: lang MUST match the language of the user's question:
    "ru" if the user asked in Russian, "en" if in English.
    Never default to "ru" for English-language questions.
    """
    article = await fetch_wikipedia(topic, lang=lang)
    if not article:
        return f"Статья по теме '{topic}' не найдена в Wikipedia."
    text = article_to_text(article)
    return f"Title: {article.title}\nURL: {article.url}\n\n{text[:3000]}"


@mcp.tool()
async def save_knowledge(title: str, content: str, source: str, lang: str = "en") -> str:
    """Saves arbitrary text into the knowledge base for later search.
    Use only if the user explicitly asks to remember/save information.
    """
    document_id = await save_document(title=title, content=content, source=source, lang=lang)
    chunks_count = await index_document(document_id, content)
    return f"Документ '{title}' сохранён (ID: {document_id}). Индексировано {chunks_count} чанков."


@mcp.tool()
def get_current_time() -> str:
    """Returns the current server date and time.
    Use ALWAYS when the user asks what time it is, what the date is,
    what day or year it is. Do NOT use search_knowledge for such questions.
    """
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")


@mcp.tool()
async def generate_image(prompt: str) -> str:
    """Generates an image from a text description (stub, available in Iteration 6).
    Use when the user explicitly asks to draw or generate a picture.
    """
    logger.info("Image generation requested (stub)", extra={"prompt": prompt})
    return f"[Stub] Image generation: '{prompt}'. Will be available in Iteration 6."


def create_sse_app():
    """Creates the MCP Server ASGI app with SSE transport."""
    return mcp.sse_app()
