from openai import AsyncOpenAI
from app.config import settings

client = AsyncOpenAI(api_key=settings.openai_api_key)

SYSTEM_PROMPT = (
    "Ты умный ассистент. Отвечай чётко и по делу. "
    "Отвечай на том языке, на котором задан вопрос."
)


async def generate_reply(user_message: str) -> str:
    response = await client.chat.completions.create(
        model=settings.openai_model,
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": user_message},
        ],
    )
    return response.choices[0].message.content or ""
