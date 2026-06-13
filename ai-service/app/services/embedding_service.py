import tiktoken
from sentence_transformers import SentenceTransformer
from app.services.db import get_pool

EMBEDDING_MODEL = "all-MiniLM-L6-v2"
CHUNK_MAX_TOKENS = 512
CHUNK_OVERLAP_TOKENS = 50

_model: SentenceTransformer | None = None


def get_model() -> SentenceTransformer:
    global _model
    if _model is None:
        _model = SentenceTransformer(EMBEDDING_MODEL)
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
    embeddings = model.encode(texts, convert_to_numpy=True)
    return embeddings.tolist()


def embed_query(text: str) -> list[float]:
    return embed_texts([text])[0]
