-- Drop old HNSW index
DROP INDEX IF EXISTS "document_chunk_embedding_hnsw_idx";

-- Change embedding dimensions from 1536 to 384
ALTER TABLE "DocumentChunk" DROP COLUMN IF EXISTS "embedding";
ALTER TABLE "DocumentChunk" ADD COLUMN "embedding" vector(384);

-- Recreate HNSW index for cosine similarity
CREATE INDEX "document_chunk_embedding_hnsw_idx"
ON "DocumentChunk"
USING hnsw ("embedding" vector_cosine_ops);
