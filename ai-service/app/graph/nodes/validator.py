import logging
import re

from app.graph.state import AgentState

logger = logging.getLogger(__name__)

SOURCE_PATTERN = re.compile(r'\[([^\]]+)\]\(([^)]+)\)')

# Markers indicating the answer relied on the knowledge base / Wikipedia
KNOWLEDGE_MARKERS = ["wikipedia.org", "[Источник", "[Title", "согласно статье"]


def validator_node(state: AgentState) -> dict:
    answer = state.get("final_answer")

    if not answer:
        logger.warning("Validator: empty answer")
        return {"validation": "empty", "retry_prompt": None}

    sources = SOURCE_PATTERN.findall(answer)
    looks_like_knowledge_based = any(m.lower() in answer.lower() for m in KNOWLEDGE_MARKERS)

    if not sources and looks_like_knowledge_based:
        logger.info("Validator: answer references knowledge but missing formatted source")
        return {
            "validation": "missing_sources",
            "retry_prompt": (
                "Твой ответ ссылается на информацию, но без корректно оформленного источника. "
                "Добавь в конец ответа ссылку в формате [Название](URL)."
            ),
        }

    logger.info("Validator: answer is valid", extra={"sources_count": len(sources)})
    return {"validation": "valid", "retry_prompt": None}
