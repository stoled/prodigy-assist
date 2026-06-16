import logging

from app.services.db import get_pool
from app.services.embedding_service import split_into_chunks, embed_texts, embed_query

logger = logging.getLogger(__name__)


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


async def source_exists(source_url: str) -> bool:
    """Проверяет — есть ли уже документ с таким source URL в БД."""
    pool = await get_pool()
    async with pool.acquire() as conn:
        row = await conn.fetchrow(
            'SELECT id FROM "Document" WHERE source = $1 LIMIT 1',
            source_url,
        )
    return row is not None


async def save_document(title: str, content: str, source: str, lang: str) -> str:
    """Сохраняет Document в PostgreSQL. Возвращает id."""
    pool = await get_pool()
    async with pool.acquire() as conn:
        row = await conn.fetchrow(
            """
            INSERT INTO "Document" (id, title, content, source, lang, "createdAt")
            VALUES (gen_random_uuid(), $1, $2, $3, $4, NOW())
            RETURNING id
            """,
            title, content, source, lang,
        )
    return str(row["id"])


async def index_wikipedia_article(article) -> tuple[str, int]:
    """
    Полный цикл: сохранить Document + проиндексировать чанки.
    Возвращает (document_id, chunks_count).
    Пропускает если статья уже проиндексирована (дедупликация по URL).
    """
    from app.wikipedia.parser import article_to_text

    if await source_exists(article.url):
        logger.info("Wikipedia article already indexed", extra={"url": article.url})
        return "", 0

    text = article_to_text(article)
    document_id = await save_document(
        title=article.title,
        content=text,
        source=article.url,
        lang=article.lang,
    )
    chunks_count = await index_document(document_id, text)
    logger.info("Wikipedia article indexed", extra={"title": article.title, "url": article.url, "chunks_count": chunks_count})
    return document_id, chunks_count
