import logging
from typing import Literal

from app.graph.state import AgentState

logger = logging.getLogger(__name__)

# Слова-маркеры, которые не требуют поиска по базе знаний
GENERAL_KEYWORDS = [
    "привет", "здравствуй", "как дела", "что ты умеешь", "кто ты",
    "hello", "hi", "how are you", "what can you do", "who are you",
]


def router_node(state: AgentState) -> dict:
    """Определяет, нужен ли поиск по RAG или можно сразу ответить."""
    message = state["user_message"].lower().strip()

    for keyword in GENERAL_KEYWORDS:
        if message.startswith(keyword) or message == keyword:
            logger.info("Router: general question, skipping RAG", extra={"query": message})
            return {"action": "skip"}

    logger.info("Router: RAG search needed", extra={"query": message})
    return {"action": "search"}
