# Tiramai RAG System - Project Plan

This document defines the architecture, rules, tech stack, folder structure, and development practices for building the Tiramai RAG system.

## Project Overview

We are building a complete Retrieval-Augmented Generation (RAG) system with:

- **Frontend**: React (clean UI, drag-and-drop file upload, chat UI)
- **Backend**: FastAPI (async, DI, caching, background tasks)
- **RAG Pipeline**: Docling (parsing + hybrid chunking), embeddings, vector DB, Gemini API for LLM
- **Storage**: PostgreSQL + pgvector
- **Memory**: Memori for conversational memory
- **Orchestration**: Docker + Docker Compose
- **Dev Environment**: Cursor with .cursor directory and strict rules per subfolder
- **Package Manager**: uv (NOT pip)

**Goal**: User uploads PDFs, DOCX, ZIPs, images, etc., system ingests them in the background, chunks + embeds them using Docling's HybridChunker, stores them, and provides a chat interface to query over the documents with persistent memory via Memori.

## Key Technical Requirements

### Frontend (React)

- Clean, minimal UI
- Drag-and-drop file upload component
- Chat interface with memory-aware conversation display
- TypeScript required
- React Query for de-duping, caching, background refetch
- Follow SOLID, DRY, KISS, YAGNI principles
- Atomic component design
- Avoid unnecessary re-renders (memo + callbacks)

### Backend (FastAPI)

- Fully async (async SQLAlchemy ORM)
- Background ingestion using BackgroundTasks
- Dependency Injection (FastAPI Depends)
- Caching layer for LLM responses, vector search, parsed document metadata
- Structured JSON logs
- Exception handling with custom exception classes
- Controller → Service → Repository → DB architecture
- Services must not know about FastAPI

### RAG Pipeline

**Components:**

1. **Docling** (https://docling-project.github.io/docling/examples/)
   - PDF parsing
   - DOCX parsing
   - ZIP unpacking
   - Hybrid chunking (use Docling's HybridChunker, not custom)
   - Markdown conversion (as recommended by Docling)

2. **Embeddings:**
   - HuggingFace embedding model: sentence-transformers/all-MiniLM-L6-v2
   - Configurable via environment variables

3. **Vector DB:**
   - PostgreSQL with pgvector
   - Store embeddings + metadata

4. **Memory System:**
   - Memori (https://github.com/GibsonAI/Memori)
   - Long-term memory
   - Short-term memory
   - Conversation history
   - Cached to avoid re-embedding repeated content

5. **LLM:**
   - Google Gemini API
   - Minimal tokens → caching response layer
   - Optimized prompt structure

**Query Flow:**
1. User sends query
2. Retrieve relevant chunks (vector search)
3. Get conversation memory (Memori)
4. Combine with memory
5. Call Gemini
6. Return reply
7. Update memory (Memori)

## Database Schema

### Tables

**documents**
- id (UUID)
- filename (VARCHAR)
- content_md (TEXT) - Markdown from Docling
- metadata (JSONB)
- created_at (TIMESTAMP)

**chunks**
- id (UUID)
- document_id (UUID, FK)
- chunk_text (TEXT)
- chunk_md (TEXT)
- embedding (vector) - pgvector, dimension from embedding model
- metadata (JSONB)
- created_at (TIMESTAMP)

**conversations**
- id (UUID)
- session_id (VARCHAR)
- user_message (TEXT)
- bot_message (TEXT)
- memory_snapshot (JSONB)
- timestamp (TIMESTAMP)

## Caching Strategy

- Cache embeddings for repeated content
- Cache LLM responses for identical queries
- Cache retrieval results
- TTL-based eviction policy
- In-memory first, Redis later

## Docker & Deployment

**Docker Compose services:**
- frontend
- backend
- postgres (with pgvector)

**Requirements:**
- Multi-stage Dockerfiles
- .dockerignore mandatory
- Lightweight images (python slim, node alpine)
- Healthchecks for each service
- Environment variables setup (no secrets exposed)

## Project Folder Structure

```
tiramai-rag/
├── frontend/
│   ├── src/
│   ├── components/
│   ├── hooks/
│   ├── api/
│   ├── utils/
│   ├── styles/
│   ├── .cursor/rules.md
│   └── Dockerfile
├── backend/
│   ├── app/
│   │   ├── api/
│   │   ├── core/
│   │   ├── services/
│   │   ├── repositories/
│   │   ├── models/
│   │   ├── schemas/
│   │   ├── vectorstore/
│   │   ├── rag/
│   │   ├── utils/
│   │   ├── logging/
│   │   └── config/
│   ├── tests/
│   ├── .cursor/rules.md
│   └── Dockerfile
├── docs/
│   ├── plan.md (this file)
│   ├── architecture.md
│   ├── api-design.md
│   └── rag-design.md
├── docker-compose.yml
├── .env.example
├── .gitignore
├── .dockerignore
├── .cursor/
│   └── root-rules.md
└── README.md
```

## Development Phases

### Phase 1 — Setup
- Create folders
- Create docs
- Create base Dockerfiles
- Setup docker-compose
- Setup Postgres + pgvector
- Setup React base project
- Setup FastAPI skeleton

### Phase 2 — RAG Ingestion
- Implement file upload API
- Background ingestion
- Docling parsing (with markdown conversion)
- Hybrid chunking (using Docling's HybridChunker)
- Embeddings + vector storage
- Caching

### Phase 3 — Chat + Memory
- Chat UI
- Chat API
- Retrieval
- RAG pipeline (Retriever + Memory + Gemini)
- Memory persistence (Memori)

### Phase 4 — Optimization
- Logging
- Rate limiting
- Caching improvements
- Query deduplication
- Token optimization

### Phase 5 — Final Integration
- End-to-end testing
- Cleanup
- Write deployment docs

## Non-Functional Requirements

- High scalability
- Async-first everywhere
- Minimal latency
- Portable setup via Docker
- Clean logs
- Debugging friendly
- Extensible RAG pipeline
- Secure file handling
- Automatic test coverage (PyTest + RTL) - focus later

## References

- Docling: https://docling-project.github.io/docling/examples/
- Memori: https://github.com/GibsonAI/Memori
- Reference Implementation: https://github.com/coleam00/ottomator-agents/tree/main/docling-rag-agent
- Video Tutorial: https://www.youtube.com/watch?v=fg0_0M8kZ8g&t=442s
- uv Package Manager: https://docs.astral.sh/uv/getting-started/installation/

