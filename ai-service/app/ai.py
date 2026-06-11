from openai import AsyncOpenAI
from app.config import settings

client = AsyncOpenAI(api_key=settings.openai_api_key)

SYSTEM_PROMPT = (
    "Ты умный ассистент. Отвечай чётко и по делу. "
    "Отвечай на том языке, на котором задан вопрос."
)


async def generate_reply(user_message: str) -> str:
    if len(user_message) > settings.max_message_length:
        raise ValueError(f"Message too long. Maximum length is {settings.max_message_length} characters.")
    
    response = await client.chat.completions.create(
        model=settings.openai_model,
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": user_message},
        ],
        max_tokens=settings.openai_max_tokens,
        timeout=settings.openai_timeout,
        temperature=settings.openai_temperature,
    )
    return response.choices[0].message.content or ""
