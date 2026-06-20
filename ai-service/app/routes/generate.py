import logging

from fastapi import APIRouter
from app.schemas.generate import GenerateRequest, GenerateResponse
from app.graph.workflow import graph
from app.exceptions import MessageTooLongError

logger = logging.getLogger(__name__)
router = APIRouter()


@router.post("/generate", response_model=GenerateResponse)
async def generate(body: GenerateRequest) -> GenerateResponse:
    try:
        initial_state = {
            "user_message": body.message,
            "lang": body.lang or "ru",
            "history": body.history or [],
            "final_answer": None,
            "error": None,
            "validation": "valid",
            "max_retries": 1,
            "retry_count": 0,
            "retry_prompt": None,
        }

        result = await graph.ainvoke(initial_state)

        if result.get("error"):
            logger.error("Graph execution error", extra={"error": result["error"]})
            raise ValueError(result["error"])

        final_answer = result.get("final_answer") or "Не удалось получить ответ."
        return GenerateResponse(reply=final_answer)

    except ValueError as e:
        raise MessageTooLongError(str(e))
