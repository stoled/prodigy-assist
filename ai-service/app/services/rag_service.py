from app.services.db import get_pool
from app.services.embedding_service import split_into_chunks, embed_texts, embed_query


async def index_document(document_id: str, text: str) -> int:
    chunks = split_into_chunks(text)
    if not chunks:
        return 0

    embeddings = embed_texts(chunks)
    pool = await get_pool()

    async with pool.acquire() as conn:
        await conn.executemany(
            """
            INSERT INTO "DocumentChunk" (id, "documentId", content, "chunkIndex", embedding, "createdAt")
            VALUES (gen_random_uuid(), $1, $2, $3, $4::vector, NOW())
            """,
            [
                (document_id, chunk, i, str(embedding))
                for i, (chunk, embedding) in enumerate(zip(chunks, embeddings))
            ],
        )

    return len(chunks)


async def search(query: str, top_k: int = 5, min_score: float = 0.5) -> list[dict]:
    embedding = embed_query(query)
    pool = await get_pool()

    async with pool.acquire() as conn:
        rows = await conn.fetch(
            """
            SELECT
                dc.id,
                dc.content,
                dc."chunkIndex",
                d.title,
                d.source,
                d.lang,
                1 - (dc.embedding <=> $1::vector) AS score
            FROM "DocumentChunk" dc
            JOIN "Document" d ON d.id = dc."documentId"
            WHERE dc.embedding IS NOT NULL
              AND 1 - (dc.embedding <=> $1::vector) >= $2
            ORDER BY dc.embedding <=> $1::vector
            LIMIT $3
            """,
            str(embedding),
            min_score,
            top_k,
        )

    return [dict(row) for row in rows]


def format_context(chunks: list[dict]) -> str:
    if not chunks:
        return ""

    parts = []
    for chunk in chunks:
        source = chunk.get("source", "unknown")
        title = chunk.get("title", "")
        content = chunk["content"]
        parts.append(f"[{title}]({source}):\n{content}")

    return "\n\n---\n\n".join(parts)
