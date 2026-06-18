import logging
import re

from app.graph.state import AgentState

logger = logging.getLogger(__name__)

SOURCE_PATTERN = re.compile(r'\[([^\]]+)\]\(([^)]+)\)')


def validator_node(state: AgentState) -> dict:
    answer = state.get("final_answer")

    if not answer:
        logger.warning("Validator: empty answer")
        return {"validation": "empty", "retry_prompt": None}

    sources = SOURCE_PATTERN.findall(answer)

    if not sources and state.get("context"):
        logger.info("Validator: answer missing sources, triggering retry")
        return {
            "validation": "missing_sources",
            "retry_prompt": (
                "Твой предыдущий ответ не содержал ссылки на источник. "
                "Обязательно добавь в конец ответа ссылку в формате [Название](URL) "
                "из предоставленного контекста."
            ),
        }

    logger.info("Validator: answer is valid", extra={"sources_count": len(sources)})
    return {"validation": "valid", "retry_prompt": None}
