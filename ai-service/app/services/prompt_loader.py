import logging
from pathlib import Path
from functools import lru_cache

logger = logging.getLogger(__name__)

PROMPTS_DIR = Path(__file__).parent.parent / "prompts"


@lru_cache(maxsize=None)
def load_prompt(name: str) -> str:
    """
    Загружает промпт из файла prompts/{name}.txt.
    Кэшируется через lru_cache — читается с диска один раз за всё время жизни процесса.
    """
    path = PROMPTS_DIR / f"{name}.txt"
    if not path.exists():
        logger.error(f"Prompt file not found: {path}")
        raise FileNotFoundError(f"Prompt file not found: {path}")

    content = path.read_text(encoding="utf-8").strip()
    logger.info(f"Loaded prompt: {name} ({len(content)} chars)")
    return content
