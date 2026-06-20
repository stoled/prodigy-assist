import logging
from typing import Literal

from langgraph.graph import StateGraph, END

from app.graph.state import AgentState
from app.graph.nodes.llm import llm_node
from app.graph.nodes.validator import validator_node

logger = logging.getLogger(__name__)


def retry_node(state: AgentState) -> dict:
    count = state.get("retry_count", 0) + 1
    logger.info("Retry node", extra={"retry_count": count})
    return {"retry_count": count}


def should_retry(state: AgentState) -> Literal["retry", "__end__"]:
    validation = state.get("validation", "valid")
    retry_count = state.get("retry_count", 0)
    max_retries = state.get("max_retries", 1)

    if validation in ("missing_sources", "empty") and retry_count < max_retries:
        logger.info("Validation: scheduling retry", extra={"validation": validation})
        return "retry"

    logger.info("Validation: finishing", extra={"validation": validation})
    return "__end__"


def build_graph() -> StateGraph:
    workflow = StateGraph(AgentState)

    workflow.add_node("llm", llm_node)
    workflow.add_node("validator", validator_node)
    workflow.add_node("retry", retry_node)

    workflow.set_entry_point("llm")

    workflow.add_edge("llm", "validator")

    workflow.add_conditional_edges(
        "validator",
        should_retry,
        {"retry": "retry", "__end__": END},
    )

    workflow.add_edge("retry", "llm")

    return workflow.compile()


graph = build_graph()
