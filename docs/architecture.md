# Tiramai RAG System - Architecture

## System Architecture Overview

```
┌─────────────┐
│   React     │  Frontend (Port 3000)
│  Frontend   │
└──────┬──────┘
       │ HTTP/REST
       │
┌──────▼──────────────────────────────────────┐
│           FastAPI Backend (Port 8000)        │
│  ┌────────────────────────────────────────┐  │
│  │  API Routes (Controllers)              │  │
│  └──────────────┬─────────────────────────┘  │
│                 │                            │
│  ┌──────────────▼────────────────────────┐  │
│  │  Service Layer                        │  │
│  │  - Upload Service                     │  │
│  │  - Document Parser (Docling)          │  │
│  │  - Chunking Service (HybridChunker)   │  │
│  │  - Embedding Service                 │  │
│  │  - Retrieval Service                 │  │
│  │  - RAG Pipeline                      │  │
│  │  - Memory Service (Memori)           │  │
│  │  - LLM Service (Gemini)              │  │
│  └──────────────┬────────────────────────┘  │
│                 │                            │
│  ┌──────────────▼────────────────────────┐  │
│  │  Repository Layer                     │  │
│  │  - Document Repository               │  │
│  │  - Chunk Repository                  │  │
│  │  - Vector Repository (pgvector)      │  │
│  │  - Conversation Repository           │  │
│  └──────────────┬────────────────────────┘  │
└─────────────────┼────────────────────────────┘
                  │
         ┌────────┴────────┐
         │                 │
┌────────▼────────┐  ┌─────▼──────────┐
│   PostgreSQL    │  │   Memori      │
│   + pgvector    │  │   (Memory)    │
└─────────────────┘  └───────────────┘
```

## Data Flow

### Document Ingestion Flow

```
1. User uploads file (PDF/DOCX/etc)
   ↓
2. Upload API receives file
   ↓
3. Background task queued
   ↓
4. Docling parses document → Markdown
   ↓
5. HybridChunker chunks markdown
   ↓
6. Embedding service generates embeddings
   ↓
7. Store in PostgreSQL + pgvector
   ↓
8. Task status updated
```

### Chat Query Flow

```
1. User sends query
   ↓
2. Chat API receives query + session_id
   ↓
3. Embed query
   ↓
4. Vector search (pgvector) → retrieve top-k chunks
   ↓
5. Memori retrieves conversation history
   ↓
6. Build prompt (chunks + memory + query)
   ↓
7. Call Gemini API (with caching)
   ↓
8. Store interaction in Memori
   ↓
9. Store in conversations table
   ↓
10. Return response to user
```

## Component Details

### Frontend Components

- **FileUpload**: Drag-and-drop component using react-dropzone
- **Chat**: Message list and input component
- **API Client**: React Query hooks for API calls

### Backend Services

- **UploadService**: Handles file uploads, queues background tasks
- **DocumentParserService**: Wraps Docling for document parsing
- **ChunkingService**: Uses Docling's HybridChunker
- **EmbeddingService**: Generates embeddings using sentence-transformers
- **VectorRepository**: Handles pgvector operations
- **RetrievalService**: Performs vector similarity search
- **MemoryService**: Wraps Memori for memory operations
- **RAGPipeline**: Orchestrates retrieval + memory + LLM
- **LLMService**: Wraps Gemini API with caching

### Database Schema

See `docs/plan.md` for detailed schema.

## Technology Choices

- **Docling**: Industry-standard document parsing with hybrid chunking
- **Memori**: Open-source memory engine for LLMs
- **pgvector**: Native PostgreSQL extension for vectors
- **uv**: Fast Python package manager
- **React Query**: Efficient data fetching and caching
- **FastAPI**: Modern async Python framework

## Security Considerations

- File upload validation (type, size)
- Input sanitization
- SQL injection prevention (SQLAlchemy handles)
- CORS configuration
- Rate limiting
- Environment variable management

## Scalability

- Async operations throughout
- Background task processing
- Caching at multiple layers
- Database connection pooling
- Horizontal scaling ready (stateless backend)

