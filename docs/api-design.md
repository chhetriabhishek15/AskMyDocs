# Tiramai RAG System - API Design

## Base URL

```
http://localhost:8000/api/v1
```

## Authentication

Currently: None (add later if needed)

## Endpoints

### Health Check

**GET** `/health`

Check if the API is running.

**Response:**
```json
{
  "status": "healthy",
  "timestamp": "2024-01-01T00:00:00Z"
}
```

---

### File Upload

**POST** `/upload`

Upload a document for ingestion.

**Request:**
- Content-Type: `multipart/form-data`
- Body: `file` (binary)

**Response:**
```json
{
  "task_id": "uuid",
  "status": "queued",
  "message": "File uploaded successfully"
}
```

**Status Codes:**
- `200`: Success
- `400`: Invalid file type or size
- `500`: Server error

---

### Task Status

**GET** `/tasks/{task_id}`

Get the status of an ingestion task.

**Response:**
```json
{
  "task_id": "uuid",
  "status": "completed", // queued, processing, completed, failed
  "progress": 100,
  "document_id": "uuid", // if completed
  "error": null // if failed
}
```

**Status Codes:**
- `200`: Success
- `404`: Task not found

---

### List Documents

**GET** `/documents`

List all ingested documents.

**Query Parameters:**
- `page` (int, default: 1)
- `page_size` (int, default: 20)

**Response:**
```json
{
  "items": [
    {
      "id": "uuid",
      "filename": "document.pdf",
      "created_at": "2024-01-01T00:00:00Z",
      "chunk_count": 42
    }
  ],
  "total": 100,
  "page": 1,
  "page_size": 20
}
```

---

### Get Document

**GET** `/documents/{document_id}`

Get details of a specific document.

**Response:**
```json
{
  "id": "uuid",
  "filename": "document.pdf",
  "content_md": "# Document content...",
  "metadata": {},
  "created_at": "2024-01-01T00:00:00Z",
  "chunk_count": 42
}
```

---

### Chat

**POST** `/chat`

Send a chat message and get AI response.

**Request:**
```json
{
  "message": "What is this document about?",
  "session_id": "session-uuid"
}
```

**Response:**
```json
{
  "reply": "This document is about...",
  "session_id": "session-uuid",
  "sources": [
    {
      "chunk_id": "uuid",
      "document_id": "uuid",
      "document_filename": "document.pdf",
      "relevance_score": 0.95,
      "preview": "Relevant text snippet..."
    }
  ],
  "timestamp": "2024-01-01T00:00:00Z"
}
```

**Status Codes:**
- `200`: Success
- `400`: Invalid request
- `500`: Server error

---

### Get Conversation History

**GET** `/conversations/{session_id}`

Get conversation history for a session.

**Query Parameters:**
- `limit` (int, default: 50)

**Response:**
```json
{
  "session_id": "session-uuid",
  "messages": [
    {
      "id": "uuid",
      "user_message": "Hello",
      "bot_message": "Hi there!",
      "timestamp": "2024-01-01T00:00:00Z"
    }
  ],
  "total": 10
}
```

---

## Error Response Format

All errors follow this format:

```json
{
  "error": {
    "code": "ERROR_CODE",
    "message": "Human-readable error message",
    "details": {} // Optional additional details
  }
}
```

**Common Error Codes:**
- `VALIDATION_ERROR`: Request validation failed
- `FILE_TOO_LARGE`: Uploaded file exceeds size limit
- `INVALID_FILE_TYPE`: File type not supported
- `TASK_NOT_FOUND`: Task ID not found
- `DOCUMENT_NOT_FOUND`: Document ID not found
- `INTERNAL_ERROR`: Server error

## Rate Limiting

- Chat endpoint: 10 requests/minute
- Upload endpoint: 5 requests/minute
- Other endpoints: 100 requests/minute

