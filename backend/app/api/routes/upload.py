"""
File upload endpoints.
"""
import os
from pathlib import Path
from fastapi import APIRouter, UploadFile, File, BackgroundTasks, Depends

import structlog

from app.core.config import settings
from app.schemas.upload import UploadResponse, TaskStatusResponse
from app.services.upload_service import UploadService
from app.services.task_tracker import get_task_tracker, TaskStatus
from app.core.exceptions import FileTooLargeError, InvalidFileTypeError, TaskNotFoundError

logger = structlog.get_logger()
router = APIRouter()


def get_upload_service() -> UploadService:
    """Dependency to get upload service."""
    upload_dir = Path(os.getenv("UPLOAD_DIR", "/app/uploads"))
    return UploadService(upload_dir=upload_dir)


async def process_document_background(
    file_path: Path,
    filename: str,
    task_id: str,
):
    """
    Background task to process uploaded document.

    Args:
        file_path: Path to uploaded file
        filename: Original filename
        task_id: Task ID for tracking
    """
    task_tracker = get_task_tracker()
    
    try:
        logger.info("background_task_started", task_id=task_id, filename=filename)
        
        # Update status to processing
        task_tracker.update_task(
            task_id=task_id,
            status=TaskStatus.PROCESSING,
            progress=0.1,
            message="Starting document processing...",
        )

        # Initialize services
        from app.services.document_parser import DocumentParserService
        from app.services.chunking_service import ChunkingService
        from app.vectorstore.chromadb_store import ChromaDBStore
        from app.repositories.chromadb_repository import ChromaDBRepository
        from app.services.ingestion_service import IngestionService

        document_parser = DocumentParserService()
        chunking_service = ChunkingService()
        
        # Initialize ChromaDB store (persistent)
        task_tracker.update_task(
            task_id=task_id,
            progress=0.2,
            message="Initializing services...",
        )
        
        chroma_store = ChromaDBStore()
        chromadb_repository = ChromaDBRepository(chroma_store)

        ingestion_service = IngestionService(
            document_parser=document_parser,
            chunking_service=chunking_service,
            chromadb_repository=chromadb_repository,
        )

        # Process document with progress callback
        def update_progress(progress: float, message: str):
            """Progress callback for ingestion service."""
            task_tracker.update_task(
                task_id=task_id,
                progress=progress,
                message=message,
            )
        
        document_id = await ingestion_service.process_document(
            file_path=file_path,
            filename=filename,
            task_id=task_id,
            progress_callback=update_progress,
        )

        # Update status to completed
        task_tracker.update_task(
            task_id=task_id,
            status=TaskStatus.COMPLETED,
            progress=1.0,
            message="Document processed successfully",
            document_id=str(document_id),
        )

        logger.info(
            "background_task_completed",
            task_id=task_id,
            filename=filename,
            document_id=str(document_id),
        )
    except Exception as e:
        error_msg = str(e)
        logger.error("background_task_failed", task_id=task_id, filename=filename, error=error_msg)
        
        # Update status to failed
        task_tracker.update_task(
            task_id=task_id,
            status=TaskStatus.FAILED,
            progress=0.0,
            message="Document processing failed",
            error=error_msg,
        )
        raise


@router.post("/upload", response_model=UploadResponse, status_code=202)
async def upload_file(
    file: UploadFile = File(...),
    background_tasks: BackgroundTasks = BackgroundTasks(),
    upload_service: UploadService = Depends(get_upload_service),
):
    """
    Upload a document for ingestion.

    Args:
        file: Uploaded file
        background_tasks: FastAPI background tasks
        upload_service: Upload service
        db: Database session

    Returns:
        Task ID and status

    Raises:
        FileTooLargeError: If file exceeds size limit
        InvalidFileTypeError: If file type is not allowed
    """
    try:
        # Validate file
        upload_service.validate_file(file.file, file.filename)

        # Save file
        file_path = upload_service.save_file(file.file, file.filename)

        # Generate task ID
        task_id = upload_service.generate_task_id()
        
        # Create task entry in tracker
        task_tracker = get_task_tracker()
        task_tracker.create_task(
            task_id=task_id,
            filename=file.filename,
            status=TaskStatus.QUEUED,
        )

        # Queue background task
        background_tasks.add_task(
            process_document_background,
            file_path=file_path,
            filename=file.filename,
            task_id=task_id,
        )

        logger.info("file_uploaded", task_id=task_id, filename=file.filename)

        return UploadResponse(
            task_id=task_id,
            status="queued",
            message="File uploaded successfully, processing started",
        )
    except (FileTooLargeError, InvalidFileTypeError):
        raise
    except Exception as e:
        logger.error("upload_failed", filename=file.filename, error=str(e))
        raise


@router.get("/upload/{task_id}/status", response_model=TaskStatusResponse)
async def get_task_status(
    task_id: str,
):
    """
    Get task status.

    Args:
        task_id: Task ID

    Returns:
        Task status information

    Raises:
        TaskNotFoundError: If task not found
    """
    task_tracker = get_task_tracker()
    task = task_tracker.get_task(task_id)
    
    if not task:
        raise TaskNotFoundError(task_id)
    
    # Convert document_id string to UUID if present
    document_id = None
    if task.get("document_id"):
        from uuid import UUID
        try:
            document_id = UUID(task["document_id"])
        except (ValueError, TypeError):
            document_id = None
    
    return TaskStatusResponse(
        task_id=task["task_id"],
        status=task["status"],
        progress=task["progress"],
        message=task["message"],
        error=task.get("error"),
        document_id=document_id,
    )


