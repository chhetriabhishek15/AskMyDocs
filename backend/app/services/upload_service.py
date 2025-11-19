"""
Upload service for handling file uploads and task management.
"""
import os
import uuid
from pathlib import Path
from typing import BinaryIO

import structlog

from app.core.config import settings
from app.core.exceptions import FileTooLargeError, InvalidFileTypeError

logger = structlog.get_logger()


class UploadService:
    """Service for handling file uploads."""

    def __init__(self, upload_dir: Path | None = None):
        """
        Initialize upload service.

        Args:
            upload_dir: Directory for storing uploaded files
        """
        import os
        default_upload_dir = os.getenv("UPLOAD_DIR", "/app/uploads")
        self.upload_dir = upload_dir or Path(default_upload_dir)
        self.upload_dir.mkdir(parents=True, exist_ok=True)
        logger.info("upload_service_initialized", upload_dir=str(self.upload_dir))

    def validate_file(self, file: BinaryIO, filename: str) -> None:
        """
        Validate uploaded file.

        Args:
            file: File object
            filename: Original filename

        Raises:
            FileTooLargeError: If file exceeds size limit
            InvalidFileTypeError: If file type is not allowed
        """
        # Check file size
        file.seek(0, os.SEEK_END)
        file_size = file.tell()
        file.seek(0)

        if file_size > settings.MAX_FILE_SIZE:
            raise FileTooLargeError(
                f"File size {file_size} exceeds maximum allowed size {settings.MAX_FILE_SIZE}"
            )

        # Check file extension
        file_ext = Path(filename).suffix.lstrip(".").lower()
        allowed_types = settings.allowed_file_types_list

        if file_ext not in allowed_types:
            raise InvalidFileTypeError(
                f"File type '{file_ext}' is not allowed. Allowed types: {', '.join(allowed_types)}"
            )

        logger.debug("file_validated", filename=filename, file_size=file_size, file_ext=file_ext)

    def save_file(self, file: BinaryIO, filename: str) -> Path:
        """
        Save uploaded file to disk.

        Args:
            file: File object
            filename: Original filename

        Returns:
            Path to saved file
        """
        # Generate unique filename
        file_id = str(uuid.uuid4())
        file_ext = Path(filename).suffix
        saved_filename = f"{file_id}{file_ext}"
        file_path = self.upload_dir / saved_filename

        # Save file
        with open(file_path, "wb") as f:
            file.seek(0)
            f.write(file.read())

        logger.info("file_saved", filename=filename, saved_path=str(file_path))
        return file_path

    def generate_task_id(self) -> str:
        """
        Generate unique task ID.

        Returns:
            Task ID string
        """
        return str(uuid.uuid4())

