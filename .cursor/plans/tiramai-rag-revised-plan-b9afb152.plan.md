<!-- b9afb152-f9f0-4be1-b91c-35db878cd2b2 81ed2ec4-804a-4ec1-a295-5f0f0257ffe0 -->
# Tiramai RAG System - Revised Implementation Plan

## Key Dependency Changes

**Updated Dependencies:**

- `docling-core>=1.0.0` (instead of `docling`)
- `fastembed` (instead of `sentence-transformers`)
- Embedding dimension: TBD based on fastembed model (currently schema uses 384, may need update)

**Rationale:**

- sentence-transformers requires 1GB+ in Docker, too large
- fastembed is lightweight and faster
- docling-core is the core parsing library without extra dependencies

## Current Status

**Completed:**

- Phase 1: Project structure, Docker setup, database schema, backend skeleton, frontend skeleton
- Frontend fixes: Error Boundary, API configuration, null checks
- Basic API routes: upload, chat, documents, conversations, health

**Not Started:**

- Phase 2: RAG ingestion pipeline (services/repositories empty)
- Phase 3: Chat interface & memory integration
- Phase 4: LLM integration & optimization
- Phase 5: Final configuration & documentation updates

## Revised Implementation Plan

### Phase 1: Project Setup & Infrastructure ✅ (Mostly Complete)

**Remaining:**

- Update `pyproject.toml` to use `docling-core` and `fastembed` (remove sentence-transformers)
- Update `backend/app/core/config.py` to use fastembed model
- Verify embedding dimension matches fastembed model (update schema if needed)

### Phase 2: RAG Ingestion Pipeline (7 todos)

**2.1 File Upload API** - `implement-file-upload-api`

- Create upload endpoint with file validation
- Background task queuing
- File: `backend/app/api/routes/upload.py` (exists, needs implementation)

**2.2 Docling-Core Integration** - `integrate-docling-core`

- Implement document parsing using `docling-core`
- Markdown conversion
- File: `backend/app/services/document_parser.py`

**2.3 Hybrid Chunking** - `implement-chunking`

- Use Docling's HybridChunker (from docling-core)
- Configurable chunk size/overlap
- File: `backend/app/services/chunking_service.py`

**2.4 FastEmbed Integration** - `implement-fastembed`

- Replace sentence-transformers with fastembed
- Determine embedding model (check fastembed defaults)
- Update embedding dimension in schema if needed
- Implement caching
- File: `backend/app/services/embedding_service.py`

**2.5 Vector Storage** - `implement-vector-storage`

- Build vector repository with pgvector operations
- Store chunks with embeddings
- File: `backend/app/repositories/vector_repository.py`

**2.6 Ingestion Pipeline** - `implement-ingestion-pipeline`

- End-to-end service: parse → chunk → embed → store
- Background task processing
- File: `backend/app/services/ingestion_service.py`

**2.7 Upload UI** - `implement-upload-ui`

- Drag-and-drop component (exists, may need updates)
- Task status polling
- File: `frontend/src/components/FileUpload.tsx`

### Phase 3: Chat Interface & Memory (5 todos)

**3.1 Chat UI** - `implement-chat-ui`

- Message list with auto-scroll
- Input with send button
- File: `frontend/src/pages/Chat.tsx` (exists, needs implementation)

**3.2 Chat API** - `implement-chat-api`

- Endpoint with request/response schemas
- File: `backend/app/api/routes/chat.py` (exists, needs implementation)

**3.3 Memori Integration** - `integrate-memori`

- Memory service using Memori
- Conversation history retrieval
- File: `backend/app/services/memory_service.py`

**3.4 Vector Retrieval** - `implement-retrieval`

- Embed query using fastembed
- Cosine similarity search with pgvector
- Top-K retrieval
- File: `backend/app/services/retrieval_service.py`

**3.5 RAG Pipeline** - `implement-rag-pipeline`

- Orchestrate: retrieval + memory + prompt building
- File: `backend/app/rag/rag_pipeline.py`

### Phase 4: LLM Integration & Optimization (5 todos)

**4.1 Gemini Integration** - `integrate-gemini`

- LLM service with Gemini API
- Response caching
- File: `backend/app/services/llm_service.py`

**4.2 Structured Logging** - `implement-logging`

- Middleware exists, verify implementation
- File: `backend/app/middleware/logging_middleware.py`

**4.3 Caching Layer** - `implement-caching`

- Cache LLM responses
- Cache embeddings (fastembed results)
- Cache retrieval results
- File: `backend/app/services/cache_service.py` or similar

**4.4 Rate Limiting** - `implement-rate-limiting`

- Middleware for API endpoints
- File: `backend/app/middleware/rate_limiting_middleware.py`

**4.5 Token Optimization** - `optimize-token-usage`

- Chunk deduplication
- Context window management
- File: `backend/app/services/token_optimizer.py`

### Phase 5: Configuration & Documentation (3 todos)

**5.1 Update Cursor Rules** - `update-cursor-rules`

- Update `.cursor/rules.md` files with new dependencies
- Document fastembed and docling-core usage

**5.2 Environment Configuration** - `update-env-config`

- Update `.env.example` with fastembed model config
- Remove sentence-transformers references

**5.3 Documentation Updates** - `update-documentation`

- Update `docs/rag-design.md` with fastembed
- Update `docs/plan.md` with dependency changes
- Update `README.md` with new tech stack

## Implementation Notes

1. **FastEmbed Usage:**
   ```python
   from fastembed import TextEmbedding
   model = TextEmbedding(model_name="BAAI/bge-small-en-v1.5")  # or default
   embeddings = list(model.embed(["text1", "text2"]))
   ```

2. **Docling-Core Usage:**

   - Check docling-core API vs full docling
   - May need to adjust parsing approach

3. **Embedding Dimension:**

   - Verify fastembed model dimension
   - Update `backend/migrations/init.sql` if dimension differs from 384
   - Update vector column type accordingly

4. **Dependency Updates:**

   - Update `pyproject.toml` (remove sentence-transformers, ensure docling-core, fastembed)
   - Regenerate `requirements.txt` if using script
   - Update Dockerfile if needed

## Files to Update

**Immediate:**

- `backend/pyproject.toml` - Update dependencies
- `backend/app/core/config.py` - Update embedding model config
- `backend/migrations/init.sql` - Verify/update embedding dimension

**During Implementation:**

- All service files in `backend/app/services/`
- All repository files in `backend/app/repositories/`
- RAG pipeline in `backend/app/rag/`
- Documentation files in `docs/`

### To-dos

- [ ] Update pyproject.toml and config.py to use docling-core and fastembed (remove sentence-transformers)
- [ ] Verify fastembed model embedding dimension and update database schema if needed
- [ ] Create upload endpoint with file validation and background task queuing
- [ ] Implement document parsing service using docling-core with markdown conversion
- [ ] Build hybrid chunking using Docling's HybridChunker from docling-core
- [ ] Create embedding service with fastembed, determine model, implement caching
- [ ] Build vector repository with pgvector operations for storing chunks and embeddings
- [ ] Create end-to-end ingestion service (parse → chunk → embed → store) with background processing
- [ ] Enhance drag-and-drop upload component with task status polling and progress tracking
- [ ] Create chat interface with message list, auto-scroll, and input handling
- [ ] Build chat endpoint with request/response schemas and error handling
- [ ] Implement memory service using Memori for conversation history and context retrieval
- [ ] Build retrieval service with fastembed query embedding and pgvector cosine similarity search
- [ ] Create RAG pipeline orchestrating retrieval, memory, prompt building, and LLM call
- [ ] Implement LLM service with Gemini API, response caching, and prompt optimization
- [ ] Build caching layer for LLM responses, fastembed embeddings, and retrieval results
- [ ] Add rate limiting middleware for API endpoints
- [ ] Implement token optimization, chunk deduplication, and context window management
- [ ] Update .cursor/rules.md files with docling-core and fastembed usage patterns
- [ ] Update .env.example with fastembed model configuration and remove sentence-transformers references
- [ ] Update docs/rag-design.md, docs/plan.md, and README.md with new dependencies and tech stack