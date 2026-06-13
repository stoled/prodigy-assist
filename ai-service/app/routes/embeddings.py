from fastapi import APIRouter, Query
from app.schemas.embeddings import (
    IndexDocumentRequest,
    IndexDocumentResponse,
    SearchResponse,
    SearchResult,
)
from app.services.rag_service import index_document, search
from app.exceptions import EmbeddingError

router = APIRouter()


@router.post("/embeddings", response_model=IndexDocumentResponse)
async def create_embeddings(body: IndexDocumentRequest) -> IndexDocumentResponse:
    try:
        chunks_count = await index_document(
            document_id=body.document_id,
            text=body.content,
        )
        return IndexDocumentResponse(
            document_id=body.document_id,
            chunks_count=chunks_count,
        )
    except Exception as e:
        raise EmbeddingError(detail=str(e))


@router.get("/search", response_model=SearchResponse)
async def search_knowledge(
    q: str = Query(..., min_length=1),
    top_k: int = Query(default=5, ge=1, le=20),
) -> SearchResponse:
    try:
        chunks = await search(query=q, top_k=top_k)
        results = [
            SearchResult(
                id=chunk["id"],
                content=chunk["content"],
                title=chunk["title"],
                source=chunk["source"],
                lang=chunk["lang"],
                score=float(chunk["score"]),
            )
            for chunk in chunks
        ]
        return SearchResponse(results=results, total=len(results))
    except Exception as e:
        raise EmbeddingError(detail=str(e))
