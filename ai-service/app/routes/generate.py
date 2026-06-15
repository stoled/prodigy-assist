from fastapi import APIRouter
from app.schemas.generate import GenerateRequest, GenerateResponse
from app.services.llm_service import generate_reply
from app.services.rag_service import search, format_context, index_wikipedia_article
from app.wikipedia.fetcher import fetch_wikipedia
from app.exceptions import MessageTooLongError

router = APIRouter()

WIKIPEDIA_FETCH_THRESHOLD = 0.5


@router.post("/generate", response_model=GenerateResponse)
async def generate(body: GenerateRequest) -> GenerateResponse:
    try:
        context: str | None = None

        if body.use_rag:
            chunks = await search(query=body.message)
            max_score = max((c["score"] for c in chunks), default=0.0)

            print(f"[RAG] chunks: {len(chunks)}, max_score: {max_score:.3f}")  # временно

            if not chunks or max_score < WIKIPEDIA_FETCH_THRESHOLD:
                lang = body.lang or None
                print(f"[Wikipedia] Fetching: '{body.message}', lang={lang}")  # временно
                article = await fetch_wikipedia(body.message, lang=lang)
                print(f"[Wikipedia] Article: {article}")  # временно

                if article:
                    await index_wikipedia_article(article)
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
