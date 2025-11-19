"""
Retrieval schemas.
"""
from typing import List, Optional
from pydantic import BaseModel, Field


class SearchRequest(BaseModel):
    """Search request schema."""

    query: str = Field(..., description="Search query text", min_length=1)
    top_k: Optional[int] = Field(None, description="Number of results to return", ge=1, le=50)
    min_score: Optional[float] = Field(None, description="Minimum similarity score", ge=0.0, le=1.0)
    document_id: Optional[str] = Field(None, description="Filter by document ID")

    class Config:
        json_schema_extra = {
            "example": {
                "query": "What is the main topic?",
                "top_k": 5,
                "min_score": 0.7,
                "document_id": None,
            }
        }


class RetrievedChunkResponse(BaseModel):
    """Retrieved chunk response schema."""

    chunk_id: str = Field(..., description="Chunk ID")
    document_id: str = Field(..., description="Document ID")
    document_filename: str = Field(..., description="Document filename")
    text: str = Field(..., description="Chunk text content")
    preview: str = Field(..., description="Text preview")
    similarity_score: float = Field(..., description="Similarity score (0.0 to 1.0)", ge=0.0, le=1.0)
    metadata: dict = Field(default_factory=dict, description="Additional metadata")


class SearchResponse(BaseModel):
    """Search response schema."""

    query: str = Field(..., description="Original query")
    results: List[RetrievedChunkResponse] = Field(..., description="Retrieved chunks")
    total: int = Field(..., description="Total number of results")

    class Config:
        json_schema_extra = {
            "example": {
                "query": "What is the main topic?",
                "total": 3,
                "results": [
                    {
                        "chunk_id": "doc-id_0",
                        "document_id": "doc-id",
                        "document_filename": "document.pdf",
                        "text": "Full chunk text...",
                        "preview": "Full chunk text...",
                        "similarity_score": 0.95,
                        "metadata": {},
                    }
                ],
            }
        }

