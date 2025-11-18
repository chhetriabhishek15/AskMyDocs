-- Enable pgvector extension
CREATE EXTENSION IF NOT EXISTS vector;

-- Create documents table
CREATE TABLE IF NOT EXISTS documents (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    filename VARCHAR(255) NOT NULL,
    content_md TEXT,
    metadata JSONB DEFAULT '{}'::jsonb,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Create chunks table with vector embedding
CREATE TABLE IF NOT EXISTS chunks (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    document_id UUID NOT NULL REFERENCES documents(id) ON DELETE CASCADE,
    chunk_text TEXT NOT NULL,
    chunk_md TEXT,
    embedding vector(384),  -- Dimension for all-MiniLM-L6-v2
    metadata JSONB DEFAULT '{}'::jsonb,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Create conversations table
CREATE TABLE IF NOT EXISTS conversations (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    session_id VARCHAR(255) NOT NULL,
    user_message TEXT NOT NULL,
    bot_message TEXT NOT NULL,
    memory_snapshot JSONB DEFAULT '{}'::jsonb,
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Create indexes for better query performance

-- Index on documents filename for quick lookups
CREATE INDEX IF NOT EXISTS idx_documents_filename ON documents(filename);
CREATE INDEX IF NOT EXISTS idx_documents_created_at ON documents(created_at);

-- Index on chunks document_id for foreign key lookups
CREATE INDEX IF NOT EXISTS idx_chunks_document_id ON chunks(document_id);
CREATE INDEX IF NOT EXISTS idx_chunks_created_at ON chunks(created_at);

-- Vector similarity search index using ivfflat (for cosine distance)
-- Note: This requires at least some data to be effective
-- We'll create it after initial data is loaded, but define it here
-- CREATE INDEX IF NOT EXISTS idx_chunks_embedding ON chunks 
-- USING ivfflat (embedding vector_cosine_ops) WITH (lists = 100);

-- For now, use a simpler index that works immediately
CREATE INDEX IF NOT EXISTS idx_chunks_embedding ON chunks 
USING ivfflat (embedding vector_cosine_ops);

-- Index on conversations session_id for quick history retrieval
CREATE INDEX IF NOT EXISTS idx_conversations_session_id ON conversations(session_id);
CREATE INDEX IF NOT EXISTS idx_conversations_timestamp ON conversations(timestamp);

-- Full-text search indexes (optional, for text-based search)
CREATE INDEX IF NOT EXISTS idx_chunks_chunk_text_gin ON chunks USING gin(to_tsvector('english', chunk_text));
CREATE INDEX IF NOT EXISTS idx_documents_content_md_gin ON documents USING gin(to_tsvector('english', content_md));


