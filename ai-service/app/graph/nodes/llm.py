import logging

from app.graph.state import AgentState
from app.services.llm_service import generate_reply

logger = logging.getLogger(__name__)


async def llm_node(state: AgentState) -> dict:
    """Генерация ответа через LLM с контекстом из RAG."""
    try:
        reply = await generate_reply(
            user_message=state["user_message"],
            history=state.get("history", []),
            context=state.get("context"),
        )
        return {"final_answer": reply}
    except Exception as exc:
        logger.error("LLM generation failed", exc_info=exc)
        return {"error": str(exc), "final_answer": None}
