from openai import AsyncOpenAI
from app.config import settings

client = AsyncOpenAI(
    base_url="https://openrouter.ai/api/v1",
    api_key=settings.ai_api_key
)

SYSTEM_PROMPT = (
    "Ты умный ассистент. Отвечай чётко и по делу. "
    "Отвечай на том языке, на котором задан вопрос."
)


async def generate_reply(user_message: str) -> str:
    if len(user_message) > settings.max_message_length:
        raise ValueError(f"Message too long. Maximum length is {settings.max_message_length} characters.")
    
    response = await client.chat.completions.create(
        model=settings.ai_model,
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": user_message},
        ],
        max_tokens=settings.ai_max_tokens,
        timeout=settings.ai_timeout,
        temperature=settings.ai_temperature,
    )
    return response.choices[0].message.content or ""
