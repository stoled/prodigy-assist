from fastapi import APIRouter
from app.schemas import GenerateRequest, GenerateResponse
from app.ai import generate_reply

router = APIRouter()


@router.post("/generate", response_model=GenerateResponse)
async def generate(body: GenerateRequest) -> GenerateResponse:
    reply = await generate_reply(body.message)
    return GenerateResponse(reply=reply)
