"""
Task status tracking service.
"""
from datetime import datetime
from typing import Dict, Optional
from uuid import UUID
import threading

import structlog

logger = structlog.get_logger()


class TaskStatus:
    """Task status enum."""
    QUEUED = "queued"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"


class TaskTracker:
    """Thread-safe task status tracker."""

    def __init__(self):
        """Initialize task tracker."""
        self._tasks: Dict[str, Dict] = {}
        self._lock = threading.Lock()
        logger.info("task_tracker_initialized")

    def create_task(
        self,
        task_id: str,
        filename: str,
        status: str = TaskStatus.QUEUED,
    ) -> None:
        """
        Create a new task entry.

        Args:
            task_id: Task ID
            filename: Original filename
            status: Initial status
        """
        with self._lock:
            self._tasks[task_id] = {
                "task_id": task_id,
                "filename": filename,
                "status": status,
                "progress": 0.0,
                "message": "Task queued",
                "error": None,
                "document_id": None,
                "created_at": datetime.utcnow().isoformat(),
                "updated_at": datetime.utcnow().isoformat(),
            }
        logger.info("task_created", task_id=task_id, filename=filename, status=status)

    def update_task(
        self,
        task_id: str,
        status: Optional[str] = None,
        progress: Optional[float] = None,
        message: Optional[str] = None,
        error: Optional[str] = None,
        document_id: Optional[str] = None,
    ) -> None:
        """
        Update task status.

        Args:
            task_id: Task ID
            status: New status
            progress: Progress (0.0 to 1.0)
            message: Status message
            error: Error message if failed
            document_id: Document ID if completed
        """
        with self._lock:
            if task_id not in self._tasks:
                logger.warning("task_not_found_for_update", task_id=task_id)
                return

            if status is not None:
                self._tasks[task_id]["status"] = status
            if progress is not None:
                self._tasks[task_id]["progress"] = max(0.0, min(1.0, progress))
            if message is not None:
                self._tasks[task_id]["message"] = message
            if error is not None:
                self._tasks[task_id]["error"] = error
            if document_id is not None:
                self._tasks[task_id]["document_id"] = document_id

            self._tasks[task_id]["updated_at"] = datetime.utcnow().isoformat()

        logger.debug(
            "task_updated",
            task_id=task_id,
            status=status,
            progress=progress,
            message=message,
        )

    def get_task(self, task_id: str) -> Optional[Dict]:
        """
        Get task status.

        Args:
            task_id: Task ID

        Returns:
            Task status dictionary or None if not found
        """
        with self._lock:
            return self._tasks.get(task_id)

    def delete_task(self, task_id: str) -> None:
        """
        Delete task entry (for cleanup).

        Args:
            task_id: Task ID
        """
        with self._lock:
            if task_id in self._tasks:
                del self._tasks[task_id]
                logger.debug("task_deleted", task_id=task_id)


# Global task tracker instance
_task_tracker = TaskTracker()


def get_task_tracker() -> TaskTracker:
    """Get global task tracker instance."""
    return _task_tracker

