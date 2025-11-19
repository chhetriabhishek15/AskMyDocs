"""
Chat schemas.
"""
from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field


class ChatMessage(BaseModel):
    """Chat message schema."""

    role: str = Field(..., description="Message role: 'user' or 'assistant'")
    content: str = Field(..., description="Message content", min_length=1)

    class Config:
        json_schema_extra = {
            "example": {
                "role": "user",
                "content": "What is the document about?",
            }
        }


class ChatRequest(BaseModel):
    """Chat request schema."""

    query: str = Field(..., description="User's question", min_length=1)
    session_id: str = Field(..., description="Session identifier for conversation history")
    top_k: Optional[int] = Field(None, description="Number of chunks to retrieve", ge=1, le=50)
    min_score: Optional[float] = Field(None, description="Minimum similarity score", ge=0.0, le=1.0)
    document_id: Optional[str] = Field(None, description="Filter search to specific document")

    class Config:
        json_schema_extra = {
            "example": {
                "query": "What is the main topic of the document?",
                "session_id": "user-123-session",
                "top_k": 5,
                "min_score": 0.5,
                "document_id": None,
            }
        }


class SourceInfo(BaseModel):
    """Source information schema."""

    chunk_id: str = Field(..., description="Chunk ID")
    document_id: str = Field(..., description="Document ID")
    document_filename: str = Field(..., description="Document filename")
    similarity_score: float = Field(..., description="Similarity score", ge=0.0, le=1.0)
    preview: str = Field(..., description="Text preview")


class ChatResponse(BaseModel):
    """Chat response schema."""

    answer: str = Field(..., description="AI-generated answer")
    sources: List[SourceInfo] = Field(..., description="Source chunks used for answer")
    session_id: str = Field(..., description="Session identifier")
    usage: Dict[str, Any] = Field(default_factory=dict, description="Token usage information")

    class Config:
        json_schema_extra = {
            "example": {
                "answer": "The document discusses the architecture of a RAG system...",
                "sources": [
                    {
                        "chunk_id": "doc-id_0",
                        "document_id": "doc-id",
                        "document_filename": "document.pdf",
                        "similarity_score": 0.95,
                        "preview": "The document discusses...",
                    }
                ],
                "session_id": "user-123-session",
                "usage": {
                    "prompt_tokens": 150,
                    "completion_tokens": 200,
                    "total_tokens": 350,
                },
            }
        }

