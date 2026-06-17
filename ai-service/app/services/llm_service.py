import logging
from pathlib import Path

from openai import AsyncOpenAI
from app.config import settings

logger = logging.getLogger(__name__)

client = AsyncOpenAI(
    api_key=settings.ai_api_key,
)

MAX_RETRIES = 3

# Загружаем system prompt из файла
PROMPTS_DIR = Path(__file__).parent.parent / "prompts"

def _load_prompt(filename: str) -> str:
    path = PROMPTS_DIR / filename
    if path.exists():
        return path.read_text(encoding="utf-8").strip()
    return ""

SYSTEM_PROMPT = _load_prompt("system.txt") or (
    "Ты умный ассистент-всезнайка. Отвечай чётко и по делу. "
    "Отвечай на том языке, на котором задан вопрос. "
    "Если используешь информацию из базы знаний — указывай источник. "
    "Если информации нет — честно сообщи, что не знаешь ответа, и не придумывай его."
)


async def generate_reply(
    user_message: str,
    history: list[dict] | None = None,
    context: str | None = None,
) -> str:
    if len(user_message) > settings.max_message_length:
        raise ValueError(
            f"Message too long. Maximum length is {settings.max_message_length} characters."
        )

    system_content = SYSTEM_PROMPT
    if context:
        system_content += f"\n\nРелевантный контекст из базы знаний:\n{context}"

    messages = [{"role": "system", "content": system_content}]

    if history:
        messages.extend(history)

    messages.append({"role": "user", "content": user_message})

    for attempt in range(MAX_RETRIES):
        response = await client.chat.completions.create(
            model=settings.ai_model,
            messages=messages,
            max_tokens=settings.ai_max_tokens,
            timeout=settings.ai_timeout,
            temperature=settings.ai_temperature,
        )
        result = response.choices[0].message.content or ""

        if result.strip():
            return result

        logger.warning(
            "Empty response from LLM",
            extra={"attempt": attempt + 1, "max_retries": MAX_RETRIES},
        )

    logger.error("All LLM retries exhausted, returning empty response")
    return ""
