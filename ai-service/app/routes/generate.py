from fastapi import APIRouter
from app.schemas.generate import GenerateRequest, GenerateResponse
from app.services.llm_service import generate_reply
from app.services.rag_service import search, format_context
from app.exceptions import MessageTooLongError

router = APIRouter()


@router.post("/generate", response_model=GenerateResponse)
async def generate(body: GenerateRequest) -> GenerateResponse:
    try:
        context: str | None = None

        if body.use_rag:
            chunks = await search(query=body.message)
            if chunks:
                context = format_context(chunks)

        reply = await generate_reply(
            user_message=body.message,
            history=body.history or [],
            context=context,
        )
        return GenerateResponse(reply=reply)
    except ValueError as e:
        raise MessageTooLongError(str(e))
