import logging
import re

from app.graph.state import AgentState

logger = logging.getLogger(__name__)

SOURCE_PATTERN = re.compile(r'\[([^\]]+)\]\(([^)]+)\)')


def validator_node(state: AgentState) -> dict:
    """Проверяет, содержит ли ответ ссылки на источники."""
    answer = state.get("final_answer")

    if not answer:
        logger.warning("Validator: empty answer")
        return {"validation": "empty"}

    sources = SOURCE_PATTERN.findall(answer)

    if not sources and state.get("context"):
        logger.info("Validator: answer missing sources, triggering retry")
        return {"validation": "missing_sources"}

    logger.info("Validator: answer is valid", extra={"sources_count": len(sources)})
    return {"validation": "valid"}
