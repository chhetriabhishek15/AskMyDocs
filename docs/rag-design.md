# Tiramai RAG System - RAG Design

## RAG Pipeline Overview

The RAG (Retrieval-Augmented Generation) pipeline combines document retrieval with LLM generation, enhanced by persistent memory.

## Components

### 1. Document Processing (Docling)

**Purpose**: Parse and chunk documents using Docling's HybridChunker.

**Flow:**
```
Raw Document (PDF/DOCX/etc)
    ↓
Docling DocumentConverter
    ↓
Markdown Output (as recommended by Docling)
    ↓
Docling HybridChunker
    ↓
Chunks with metadata
```

**Configuration:**
- Chunk size: Configurable via environment variables
- Overlap: Configurable via environment variables
- Use Docling's built-in hybrid chunking strategy (not custom)

**References:**
- Docling Examples: https://docling-project.github.io/docling/examples/
- Reference Implementation: https://github.com/coleam00/ottomator-agents/tree/main/docling-rag-agent

### 2. Embedding Generation

**Model**: `sentence-transformers/all-MiniLM-L6-v2`
- Dimension: 384
- Lightweight and fast
- Good quality for semantic search

**Process:**
1. Take chunk text
2. Generate embedding using sentence-transformers
3. Cache embedding (hash-based key)
4. Store in pgvector

**Caching:**
- Hash chunk text → cache key
- Store embeddings in memory (Redis later)
- TTL: 24 hours

### 3. Vector Storage (pgvector)

**Database**: PostgreSQL with pgvector extension

**Schema:**
```sql
CREATE TABLE chunks (
    id UUID PRIMARY KEY,
    document_id UUID REFERENCES documents(id),
    chunk_text TEXT,
    chunk_md TEXT,
    embedding vector(384),  -- Dimension from embedding model
    metadata JSONB,
    created_at TIMESTAMP
);

CREATE INDEX ON chunks USING ivfflat (embedding vector_cosine_ops);
```

**Operations:**
- Store: Insert chunk with embedding
- Search: Cosine similarity search
- Top-K retrieval: Get most similar chunks

### 4. Memory Management (Memori)

**Library**: Memori from GibsonAI (https://github.com/GibsonAI/Memori)

**Purpose:**
- Long-term memory: Store conversation history
- Short-term memory: Recent context
- Entity extraction: Extract important entities
- Context prioritization: Retrieve relevant memories

**Integration:**
```python
from memori import Memori

memori = Memori(
    database_connect="postgresql://...",
    conscious_ingest=True,  # Short-term working memory
    auto_ingest=True,       # Dynamic search per query
)
memori.enable()
```

**Usage:**
1. Before LLM call: Retrieve relevant memories for session
2. Inject memories into prompt context
3. After LLM call: Store interaction in Memori
4. Memori handles entity extraction and categorization

### 5. Retrieval Process

**Query Flow:**
```
User Query
    ↓
Embed Query (same model as chunks)
    ↓
Vector Search (pgvector cosine similarity)
    ↓
Top-K Chunks (default: 5)
    ↓
Rank by relevance score
    ↓
Return chunks with metadata
```

**Parameters:**
- `top_k`: Number of chunks to retrieve (default: 5)
- `min_score`: Minimum similarity score (optional filter)

### 6. RAG Pipeline Orchestration

**Complete Flow:**
```
1. User Query + Session ID
    ↓
2. Embed Query
    ↓
3. Vector Search → Retrieve Top-K Chunks
    ↓
4. Memori → Retrieve Conversation History
    ↓
5. Build Prompt:
   - System prompt
   - Retrieved chunks (context)
   - Conversation history (from Memori)
   - User query
    ↓
6. Call Gemini API (with caching)
    ↓
7. Store Interaction:
   - Memori: Store in memory system
   - Database: Store in conversations table
    ↓
8. Return Response + Sources
```

### 7. LLM Integration (Gemini)

**API**: Google Gemini API

**Configuration:**
- Model: `gemini-pro` (or latest)
- Temperature: Configurable
- Max tokens: Configurable
- Caching: Cache responses for identical queries

**Prompt Template:**
```
You are a helpful assistant. Answer the user's question based on the provided context.

Context from Documents:
{retrieved_chunks}

Conversation History:
{memory_context}

User Question: {query}

Answer based on the context provided. If the context doesn't contain enough information, say so.
```

**Caching:**
- Hash prompt → cache key
- Store response in cache
- TTL: 1 hour
- Check cache before API call

## Configuration

**Environment Variables:**
```env
# Embedding Model
EMBEDDING_MODEL=sentence-transformers/all-MiniLM-L6-v2
EMBEDDING_DIMENSION=384

# Chunking (Docling HybridChunker)
CHUNK_SIZE=512
CHUNK_OVERLAP=50

# Retrieval
TOP_K_RETRIEVAL=5
MIN_SIMILARITY_SCORE=0.7

# LLM
GEMINI_API_KEY=your_key_here
GEMINI_MODEL=gemini-pro
GEMINI_TEMPERATURE=0.7
GEMINI_MAX_TOKENS=2048

# Memory (Memori)
MEMORI_DATABASE_CONNECTION=postgresql://...
MEMORI_CONSCIOUS_INGEST=true
MEMORI_AUTO_INGEST=true
```

## Optimization Strategies

1. **Token Optimization:**
   - Truncate chunks to fit context window
   - Remove redundant chunks (high similarity)
   - Compress memory context

2. **Caching:**
   - Embeddings: 24 hours TTL
   - LLM responses: 1 hour TTL
   - Retrieval results: 30 minutes TTL

3. **Query Deduplication:**
   - Track in-flight requests
   - Return cached result for duplicate queries

4. **Chunk Filtering:**
   - Filter chunks by minimum similarity score
   - Remove chunks that are too short/long

## Error Handling

- **Docling Parsing Errors**: Log error, return user-friendly message
- **Embedding Generation Errors**: Retry with exponential backoff
- **Vector Search Errors**: Fallback to keyword search
- **Memori Errors**: Continue without memory context, log error
- **Gemini API Errors**: Retry with exponential backoff, return error message

## Future Enhancements

- Re-ranking: Use cross-encoder for better chunk ranking
- Multi-query: Generate multiple query variations
- Query expansion: Expand query with synonyms
- Hybrid search: Combine vector + keyword search
- Redis caching: Move from in-memory to Redis

