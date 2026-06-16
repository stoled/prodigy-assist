import logging

from fastapi import APIRouter
from app.schemas.generate import GenerateRequest, GenerateResponse
from app.services.llm_service import generate_reply
from app.services.rag_service import search, format_context, index_wikipedia_article
from app.wikipedia.fetcher import fetch_wikipedia
from app.exceptions import MessageTooLongError

logger = logging.getLogger(__name__)
router = APIRouter()

WIKIPEDIA_FETCH_THRESHOLD = 0.7  # Lower threshold for semantic similarity (all-MiniLM-L6-v2)


@router.post("/generate", response_model=GenerateResponse)
async def generate(body: GenerateRequest) -> GenerateResponse:
    try:
        context: str | None = None

        if body.use_rag:
            # Search with lower threshold (0.2) to include more results, Wikipedia fallback at 0.5
            chunks = await search(query=body.message, min_score=0.2)
            max_score = max((c["score"] for c in chunks), default=0.0)
            logger.info(
                f"RAG search completed: {len(chunks)} chunks, max_score={max_score:.3f}",
                extra={"user_message": body.message, "chunks": len(chunks), "max_score": max_score},
            )

            if not chunks or max_score < WIKIPEDIA_FETCH_THRESHOLD:
                logger.info(
                    f"RAG fallback to Wikipedia: {len(chunks)} chunks, max_score={max_score:.3f}, lang={body.lang}",
                    extra={"user_message": body.message, "lang": body.lang, "chunks": len(chunks), "max_score": max_score},
                )
                try:
                    article = await fetch_wikipedia(body.message, lang=body.lang)
                except Exception as exc:
                    logger.warning("Wikipedia fetch failed", exc_info=exc)
                    article = None

                if article:
                    await index_wikipedia_article(article)
                    chunks = await search(query=body.message, min_score=0.2)
                else:
                    logger.info(
                        "Wikipedia fallback returned no article",
                        extra={"user_message": body.message, "lang": body.lang},
                    )

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
