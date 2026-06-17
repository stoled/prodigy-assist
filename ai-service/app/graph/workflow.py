import logging
from typing import Literal

from langgraph.graph import StateGraph, END

from app.graph.state import AgentState
from app.graph.nodes.router import router_node
from app.graph.nodes.rag_search import rag_search_node
from app.graph.nodes.wikipedia_fetch import wikipedia_fetch_node
from app.graph.nodes.llm import llm_node
from app.graph.nodes.validator import validator_node

logger = logging.getLogger(__name__)


def should_search(state: AgentState) -> Literal["rag_search", "llm"]:
    """Определяет маршрут после роутера."""
    action = state.get("action", "search")
    return "rag_search" if action == "search" else "llm"


def should_fetch_wikipedia(state: AgentState) -> Literal["wikipedia_fetch", "llm"]:
    """Проверяет, нужно ли фетчить Wikipedia."""
    # Уже пробовали — не зацикливаемся
    if state.get("wikipedia_attempted"):
        logger.info("Wikipedia already attempted, skipping to LLM")
        return "llm"

    chunks = state.get("retrieved_chunks", [])
    max_score = max((c["score"] for c in chunks), default=0.0)

    if not chunks or max_score < 0.7:
        return "wikipedia_fetch"
    return "llm"


def should_retry(state: AgentState) -> Literal["llm", "rag_search", "__end__"]:
    """Определяет действие после валидатора."""
    validation = state.get("validation", "valid")
    retry_count = state.get("rag_retry_count", 0)
    max_retries = state.get("max_rag_retries", 1)

    if validation == "missing_sources" and retry_count < max_retries:
        logger.info("Validation: retrying LLM with stricter source prompting")
        state["rag_retry_count"] = retry_count + 1
        return "llm"

    if validation == "empty":
        if retry_count < max_retries:
            logger.warning(
                "Validation: empty answer, retrying with RAG search",
                extra={"retry": retry_count + 1, "max_retries": max_retries},
            )
            state["rag_retry_count"] = retry_count + 1
            return "rag_search"
        logger.error("Validation: empty answer, max retries exhausted, finishing")
        return "__end__"

    logger.info("Validation: answer is valid, finishing")
    return "__end__"


def build_graph() -> StateGraph:
    """Собирает и компилирует граф."""
    workflow = StateGraph(AgentState)

    # Регистрируем узлы
    workflow.add_node("router", router_node)
    workflow.add_node("rag_search", rag_search_node)
    workflow.add_node("wikipedia_fetch", wikipedia_fetch_node)
    workflow.add_node("llm", llm_node)
    workflow.add_node("validator", validator_node)

    # Начало — всегда роутер
    workflow.set_entry_point("router")

    # Условные переходы
    workflow.add_conditional_edges(
        "router",
        should_search,
        {
            "rag_search": "rag_search",
            "llm": "llm",
        },
    )

    workflow.add_conditional_edges(
        "rag_search",
        should_fetch_wikipedia,
        {
            "wikipedia_fetch": "wikipedia_fetch",
            "llm": "llm",
        },
    )

    workflow.add_edge("wikipedia_fetch", "rag_search")

    workflow.add_edge("llm", "validator")

    workflow.add_conditional_edges(
        "validator",
        should_retry,
        {
            "llm": "llm",
            "rag_search": "rag_search",
            "__end__": END,
        },
    )

    return workflow.compile()


# Синглтон графа
graph = build_graph()
