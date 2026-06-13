from pydantic import BaseModel


class IndexDocumentRequest(BaseModel):
    document_id: str
    title: str
    content: str


class IndexDocumentResponse(BaseModel):
    document_id: str
    chunks_count: int
    status: str = "indexed"


class SearchResult(BaseModel):
    id: str
    content: str
    title: str
    source: str
    lang: str
    score: float


class SearchResponse(BaseModel):
    results: list[SearchResult]
    total: int
