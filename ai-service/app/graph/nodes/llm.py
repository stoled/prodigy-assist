import logging

from app.graph.state import AgentState
from app.services.llm_service import generate_reply

logger = logging.getLogger(__name__)


async def llm_node(state: AgentState) -> dict:
    try:
        user_message = state["user_message"]

        # При retry добавляем напоминание об источнике
        retry_prompt = state.get("retry_prompt")
        if retry_prompt:
            user_message = f"{user_message}\n\n[Системное напоминание: {retry_prompt}]"

        reply = await generate_reply(
            user_message=user_message,
            history=state.get("history", []),
            context=state.get("context"),
        )
        return {"final_answer": reply}
    except Exception as exc:
        logger.error("LLM generation failed", exc_info=exc)
        return {"error": str(exc), "final_answer": None}
