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
        # Инициализируем состояние графа
        initial_state = {
            "user_message": body.message,
            "lang": body.lang or "en",
            "history": body.history or [],
            "retrieved_chunks": [],
            "context": None,
            "wikipedia_fetched": False,
            "wikipedia_attempted": False,
            "final_answer": None,
            "error": None,
        }

        # Запускаем граф
        result = await graph.ainvoke(initial_state)

        # Проверяем ошибки
        if result.get("error"):
            logger.error("Graph execution error", extra={"error": result["error"]})
            raise ValueError(result["error"])

        final_answer = result.get("final_answer") or "Не удалось получить ответ."

        return GenerateResponse(reply=final_answer)

    except ValueError as e:
        raise MessageTooLongError(str(e))
