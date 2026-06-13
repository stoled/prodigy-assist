from fastapi import APIRouter
from app.schemas.generate import GenerateRequest, GenerateResponse
from app.services.llm_service import generate_reply
from app.exceptions import MessageTooLongError

router = APIRouter()


@router.post("/generate", response_model=GenerateResponse)
async def generate(body: GenerateRequest) -> GenerateResponse:
    try:
        reply = await generate_reply(
            user_message=body.message,
            history=body.history or [],
        )
        return GenerateResponse(reply=reply)
    except ValueError as e:
        raise MessageTooLongError(str(e))
