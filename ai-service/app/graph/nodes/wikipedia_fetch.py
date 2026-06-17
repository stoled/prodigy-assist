import logging

from app.graph.state import AgentState
from app.wikipedia.fetcher import fetch_wikipedia
from app.services.rag_service import index_wikipedia_article, search, format_context

logger = logging.getLogger(__name__)

WIKIPEDIA_FETCH_THRESHOLD = 0.7


async def wikipedia_fetch_node(state: AgentState) -> dict:
    """Загрузка статьи из Wikipedia, индексация и повторный поиск."""
    chunks = state.get("retrieved_chunks", [])
    max_score = max((c["score"] for c in chunks), default=0.0)

    if chunks and max_score >= WIKIPEDIA_FETCH_THRESHOLD:
        logger.info("Wikipedia fetch: skipped, RAG score is sufficient")
        return {}

    try:
        article = await fetch_wikipedia(state["user_message"], lang=state["lang"])
    except Exception as exc:
        logger.warning("Wikipedia fetch failed", exc_info=exc)
        return {"wikipedia_attempted": True, "error": str(exc)}

    if not article:
        logger.info("Wikipedia: no article found")
        return {"wikipedia_attempted": True}

    await index_wikipedia_article(article)

    # Повторный поиск после индексации
    new_chunks = await search(query=state["user_message"], top_k=5, min_score=0.5)
    new_context = format_context(new_chunks) if new_chunks else None

    return {
        "wikipedia_attempted": True,
        "wikipedia_fetched": True,
        "retrieved_chunks": new_chunks,
        "context": new_context,
    }
