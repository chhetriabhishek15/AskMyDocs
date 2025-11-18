"""
Custom exception classes for the application.
"""


class BaseAPIException(Exception):
    """Base exception for all API errors."""

    def __init__(
        self,
        message: str,
        status_code: int = 500,
        error_code: str = "INTERNAL_ERROR",
        details: dict = None,
    ):
        """
        Initialize API exception.

        Args:
            message: Human-readable error message
            status_code: HTTP status code
            error_code: Machine-readable error code
            details: Additional error details
        """
        self.message = message
        self.status_code = status_code
        self.error_code = error_code
        self.details = details or {}
        super().__init__(self.message)


class ValidationError(BaseAPIException):
    """Validation error exception."""

    def __init__(self, message: str, details: dict = None):
        super().__init__(
            message=message,
            status_code=400,
            error_code="VALIDATION_ERROR",
            details=details,
        )


class FileTooLargeError(BaseAPIException):
    """File size exceeds limit."""

    def __init__(self, message: str = "File size exceeds maximum allowed size"):
        super().__init__(
            message=message,
            status_code=400,
            error_code="FILE_TOO_LARGE",
        )


class InvalidFileTypeError(BaseAPIException):
    """Invalid file type."""

    def __init__(self, message: str = "File type not supported"):
        super().__init__(
            message=message,
            status_code=400,
            error_code="INVALID_FILE_TYPE",
        )


class NotFoundError(BaseAPIException):
    """Resource not found."""

    def __init__(self, message: str = "Resource not found", details: dict = None):
        super().__init__(
            message=message,
            status_code=404,
            error_code="NOT_FOUND",
            details=details,
        )


class TaskNotFoundError(NotFoundError):
    """Task not found."""

    def __init__(self, task_id: str):
        super().__init__(
            message=f"Task {task_id} not found",
            details={"task_id": task_id},
        )


class DocumentNotFoundError(NotFoundError):
    """Document not found."""

    def __init__(self, document_id: str):
        super().__init__(
            message=f"Document {document_id} not found",
            details={"document_id": document_id},
        )


