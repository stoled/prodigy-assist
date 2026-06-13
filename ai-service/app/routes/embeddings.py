from fastapi import APIRouter
from app.schemas.embeddings import IndexDocumentRequest, IndexDocumentResponse
from app.services.rag_service import index_document
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
