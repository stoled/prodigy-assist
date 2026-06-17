import logging

from app.graph.state import AgentState
from app.services.rag_service import search, format_context

logger = logging.getLogger(__name__)


async def rag_search_node(state: AgentState) -> dict:
    """Поиск релевантных чанков в pgvector."""
    chunks = await search(
        query=state["user_message"],
        top_k=5,
        min_score=0.5,
    )

    max_score = max((c["score"] for c in chunks), default=0.0)
    logger.info(
        "RAG search completed",
        extra={"chunks": len(chunks), "max_score": round(max_score, 3)},
    )

    context = format_context(chunks) if chunks else None

    return {
        "retrieved_chunks": chunks,
        "context": context,
    }
