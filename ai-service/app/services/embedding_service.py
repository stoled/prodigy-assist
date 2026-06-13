import tiktoken
from fastembed import TextEmbedding
from app.services.db import get_pool

EMBEDDING_MODEL = "sentence-transformers/all-MiniLM-L6-v2"
CHUNK_MAX_TOKENS = 512
CHUNK_OVERLAP_TOKENS = 50

_model: TextEmbedding | None = None


def get_model() -> TextEmbedding:
    global _model
    if _model is None:
        _model = TextEmbedding(EMBEDDING_MODEL)
    return _model


def split_into_chunks(text: str) -> list[str]:
    enc = tiktoken.get_encoding("cl100k_base")
    tokens = enc.encode(text)
    chunks = []
    start = 0

    while start < len(tokens):
        end = min(start + CHUNK_MAX_TOKENS, len(tokens))
        chunk_tokens = tokens[start:end]
        chunks.append(enc.decode(chunk_tokens))
        start += CHUNK_MAX_TOKENS - CHUNK_OVERLAP_TOKENS

    return chunks


def embed_texts(texts: list[str]) -> list[list[float]]:
    model = get_model()
    embeddings = list(model.embed(texts))
    return [e.tolist() for e in embeddings]


def embed_query(text: str) -> list[float]:
    return embed_texts([text])[0]
