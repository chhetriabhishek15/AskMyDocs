# Complete RAG Flow Documentation

## Architecture Overview

```
┌─────────────┐
│   Upload    │
│   Document  │
└──────┬──────┘
       │
       ▼
┌─────────────────┐
│  Document       │
│  Processing     │
│  (Background)   │
└──────┬──────────┘
       │
       ▼
┌─────────────────┐
│  ChromaDB       │
│  (Vector Store) │
└──────┬──────────┘
       │
       ▼
┌─────────────────┐
│  Chat Request   │
│  (Session ID)   │
└──────┬──────────┘
       │
       ▼
┌─────────────────────────────────────┐
│         RAG Pipeline                │
│  ┌───────────────────────────────┐  │
│  │ 1. Retrieval Service          │  │
│  │    - Vector similarity search │  │
│  │    - Get relevant chunks       │  │
│  └──────────────┬────────────────┘  │
│                 │                    │
│  ┌──────────────▼────────────────┐  │
│  │ 2. Memory Service (Memori)    │  │
│  │    - Get conversation history │  │
│  │    - Session-based memory     │  │
│  └──────────────┬────────────────┘  │
│                 │                    │
│  ┌──────────────▼────────────────┐  │
│  │ 3. Prompt Templates           │  │
│  │    - app/rag/prompts/          │  │
│  │    - Build RAG prompt          │  │
│  └──────────────┬────────────────┘  │
│                 │                    │
│  ┌──────────────▼────────────────┐  │
│  │ 4. LLM Service (LangChain)    │  │
│  │    - Generate response         │  │
│  │    - With Memori callbacks     │  │
│  └──────────────┬────────────────┘  │
│                 │                    │
│  ┌──────────────▼────────────────┐  │
│  │ 5. Store in Memory            │  │
│  │    - Save user query          │  │
│  │    - Save assistant response  │  │
│  └──────────────────────────────┘  │
└─────────────────────────────────────┘
       │
       ▼
┌─────────────────┐
│  Chat Response  │
│  + Sources      │
└─────────────────┘
```

## Complete Flow: Upload → Chat

### Step 1: Document Upload

**Endpoint**: `POST /api/v1/upload`

**Process**:
1. User uploads a document (PDF, DOCX, MD, etc.)
2. File is validated and saved temporarily
3. Background task is created with status `QUEUED`
4. Task ID is returned to client

**Response**:
```json
{
  "task_id": "550e8400-e29b-41d4-a716-446655440000",
  "status": "queued",
  "message": "File uploaded successfully, processing started"
}
```

### Step 2: Document Processing (Background)

**Process**:
1. **Parsing**: Document is parsed using `docling` → `DoclingDocument`
2. **Chunking**: `HybridChunker` creates semantic chunks with token limits
3. **Storage**: Chunks are stored in ChromaDB with:
   - Document ID
   - Chunk text
   - Metadata (filename, chunk_index, etc.)
   - Embeddings (handled by ChromaDB)

**Status Updates**:
- `QUEUED` → `PROCESSING` (0% → 100%)
- `PROCESSING` → `COMPLETED` (with document_id)
- Or `PROCESSING` → `FAILED` (with error message)

**Check Status**: `GET /api/v1/upload/{task_id}/status`

### Step 3: Chat Request

**Endpoint**: `POST /api/v1/chat`

**Request**:
```json
{
  "query": "What is the document about?",
  "session_id": "user-123-session",
  "top_k": 5,
  "min_score": 0.5,
  "document_id": null
}
```

**Internal Flow**:

#### 3.1 Retrieval Phase
```python
# app/rag/pipeline.py → generate()
context_chunks = await retrieval_service.retrieve_with_context(
    query_text=query,
    top_k=top_k,
    min_score=min_score,
    document_id=document_id,
)
```
- Uses ChromaDB vector similarity search
- Returns chunks with similarity scores
- Filters by `min_score` threshold

#### 3.2 Memory Phase
```python
# Get conversation history from Memori
conversation_history = memory_service.get_conversation_history(
    session_id=session_id,
    limit=5,
)
```
- Retrieves previous messages for the session
- Memori handles this automatically via `memori.enable()`

#### 3.3 Prompt Building Phase
```python
# app/rag/prompts/templates.py → RAGPromptTemplate.build()
prompt = prompt_template.build(
    user_query=query,
    context_chunks=context_chunks,
    conversation_history=conversation_history,
)
```

**Prompt Structure**:
```
[System Prompt from app/rag/prompts/system_prompts.py]

## Context Documents:

### Document 1: filename.pdf (Relevance: 0.85)
[Chunk text content...]

### Document 2: filename.pdf (Relevance: 0.78)
[Chunk text content...]

## Previous Conversation:

User: [Previous query]
Assistant: [Previous response]

## User Question:
[Current query]

## Your Response:
```

**Important**: Prompt building happens in `app/rag/prompts/templates.py`, NOT in `llm_service.py`

#### 3.4 LLM Generation Phase
```python
# app/services/llm_service.py → generate()
llm_response = await llm_service.generate(
    prompt=prompt,  # Already built by RAGPromptTemplate
    use_cache=True,
    callbacks=memori_callbacks,  # For Memori integration
)
```

**LLM Service Responsibilities**:
- ✅ Generate responses using LangChain + Gemini
- ✅ Handle caching
- ✅ Support LangChain callbacks
- ❌ **NOT responsible for prompt building** (that's in `app/rag/prompts/`)

#### 3.5 Memory Storage Phase
```python
# Store conversation in Memori
memory_service.store_message(session_id, "user", query)
memory_service.store_message(session_id, "assistant", response.text)
```

### Step 4: Chat Response

**Response**:
```json
{
  "answer": "The document discusses the architecture of a RAG system...",
  "sources": [
    {
      "chunk_id": "doc-id_0",
      "document_id": "doc-id",
      "document_filename": "document.pdf",
      "similarity_score": 0.85,
      "preview": "The document discusses..."
    }
  ],
  "session_id": "user-123-session",
  "usage": {
    "prompt_tokens": 150,
    "completion_tokens": 200,
    "total_tokens": 350
  }
}
```

## Session Persistence

### How It Works

1. **First Query**:
   - User sends query with `session_id: "user-123"`
   - No conversation history exists
   - Memori stores: `(session_id, "user", query)`
   - Memori stores: `(session_id, "assistant", response)`

2. **Second Query** (same session):
   - User sends query with `session_id: "user-123"`
   - Memori retrieves previous conversation
   - Prompt includes conversation history
   - LLM has context from previous exchange
   - New messages are stored

3. **Third Query** (same session):
   - Full conversation history available
   - Context-aware responses
   - Natural conversation flow

### Memori Integration

- **Database**: SQLite (default) or PostgreSQL
- **Storage Location**: `{CHROMA_DB_PATH}/memory.db` (SQLite fallback)
- **Modes**:
  - `conscious_ingest=True`: Short-term working memory
  - `auto_ingest=True`: Dynamic search per query
- **Integration**: Via LangChain callbacks (`memori.enable()`)

## File Organization

```
backend/app/
├── services/
│   └── llm_service.py          # ✅ LLM generation only (NO prompt building)
│
├── rag/
│   ├── pipeline.py             # Orchestrates entire RAG flow
│   ├── retrieval.py            # Vector similarity search
│   ├── memory_service.py       # Memori integration
│   │
│   ├── prompts/                # ✅ ALL PROMPT LOGIC HERE
│   │   ├── templates.py        # RAGPromptTemplate class
│   │   └── system_prompts.py   # System prompt definitions
│   │
│   └── utils/
│       ├── context_builder.py  # Format chunks into context
│       └── prompt_builder.py   # Build prompts from templates
│
└── api/routes/
    └── chat.py                 # Chat endpoint using RAG pipeline
```

## Key Principles

1. **Separation of Concerns**:
   - `llm_service.py`: Only generates responses (LangChain + Gemini)
   - `app/rag/prompts/`: All prompt building logic
   - `app/rag/pipeline.py`: Orchestrates everything

2. **Session Management**:
   - Each user has a unique `session_id`
   - Memori stores conversation per session
   - History is automatically included in prompts

3. **Source Attribution**:
   - Every response includes source chunks
   - Sources show document name and similarity score
   - Users can verify information

## Testing the Complete Flow

Run the end-to-end test:
```bash
cd backend
python test_end_to_end_flow.py
```

This test:
1. ✅ Uploads a test document
2. ✅ Waits for processing
3. ✅ Sends 3 chat queries with same session_id
4. ✅ Verifies session persistence
5. ✅ Confirms prompt templates are used correctly
6. ✅ Verifies LLM service doesn't build prompts

## API Endpoints Summary

| Endpoint | Method | Purpose |
|----------|--------|---------|
| `/api/v1/upload` | POST | Upload document |
| `/api/v1/upload/{task_id}/status` | GET | Check processing status |
| `/api/v1/chat` | POST | Send chat query |
| `/api/v1/documents` | GET | List uploaded documents |
| `/api/v1/documents/search` | POST | Search documents (direct) |

## Environment Variables

```env
# Gemini API
GEMINI_API_KEY=your_key_here
GEMINI_MODEL=gemini-pro

# ChromaDB
CHROMA_DB_PATH=./chroma_db
CHROMA_COLLECTION_NAME=documents

# Memori
MEMORI_DATABASE_CONNECTION=sqlite:///memory.db  # Optional
MEMORI_USE_SQLITE_FALLBACK=true
MEMORI_CONSCIOUS_INGEST=true
MEMORI_AUTO_INGEST=true
```

