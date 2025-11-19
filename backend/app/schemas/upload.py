"""
Upload schemas.
"""
from uuid import UUID
from pydantic import BaseModel, Field


class UploadResponse(BaseModel):
    """Upload response schema."""

    task_id: str = Field(..., description="Task ID for tracking upload progress")
    status: str = Field(..., description="Task status")
    message: str = Field(..., description="Status message")

    class Config:
        json_schema_extra = {
            "example": {
                "task_id": "550e8400-e29b-41d4-a716-446655440000",
                "status": "queued",
                "message": "File uploaded successfully, processing started",
            }
        }


class TaskStatusResponse(BaseModel):
    """Task status response schema."""

    task_id: str = Field(..., description="Task ID")
    status: str = Field(..., description="Task status: queued, processing, completed, failed")
    progress: float = Field(0.0, ge=0.0, le=1.0, description="Progress percentage (0.0 to 1.0)")
    message: str = Field(..., description="Status message")
    error: str | None = Field(None, description="Error message if failed")
    document_id: UUID | None = Field(None, description="Document ID if completed")

    class Config:
        json_schema_extra = {
            "example": {
                "task_id": "550e8400-e29b-41d4-a716-446655440000",
                "status": "processing",
                "progress": 0.5,
                "message": "Processing document...",
                "error": None,
                "document_id": None,
            }
        }

