import logging

from openai import AsyncOpenAI
from app.config import settings
from app.services.prompt_loader import load_prompt

logger = logging.getLogger(__name__)

client = AsyncOpenAI(
    api_key=settings.ai_api_key,
)

MAX_RETRIES = 3


async def generate_reply(
    user_message: str,
    history: list[dict] | None = None,
    context: str | None = None,
) -> str:
    if len(user_message) > settings.max_message_length:
        raise ValueError(
            f"Message too long. Maximum length is {settings.max_message_length} characters."
        )

    system_content = load_prompt("system")
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
