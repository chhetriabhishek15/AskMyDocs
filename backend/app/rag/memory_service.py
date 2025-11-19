"""
Memory service for conversation history using Memori.
"""
from typing import List, Dict, Any, Optional
from pathlib import Path

import structlog

from app.core.config import settings

logger = structlog.get_logger()


class MemoryService:
    """Service for managing conversation memory using Memori."""

    def __init__(self):
        """Initialize Memori memory service."""
        self.memori = None
        self._initialized = False
        self._init_error = None

        try:
            from memori import Memori

            # Determine database connection string
            db_connection = self._get_database_connection()

            # Initialize Memori
            self.memori = Memori(
                database_connect=db_connection,
                conscious_ingest=settings.MEMORI_CONSCIOUS_INGEST,
                auto_ingest=settings.MEMORI_AUTO_INGEST,
                openai_api_key=settings.GEMINI_API_KEY,  # Memori may need API key for embeddings
            )

            # Enable Memori (intercepts LLM calls)
            self.memori.enable()

            self._initialized = True
            logger.info(
                "memori_initialized",
                database=db_connection.split("@")[-1] if "@" in db_connection else db_connection,
                conscious_ingest=settings.MEMORI_CONSCIOUS_INGEST,
                auto_ingest=settings.MEMORI_AUTO_INGEST,
            )

        except ImportError:
            self._init_error = "memorisdk not installed"
            logger.warning("memori_not_available", error=self._init_error)
        except Exception as e:
            self._init_error = str(e)
            logger.error("memori_init_failed", error=str(e))

    def _get_database_connection(self) -> str:
        """
        Get database connection string for Memori.

        Returns:
            Database connection string (SQLite or PostgreSQL)
        """
        # If MEMORI_DATABASE_CONNECTION is set, use it
        if settings.MEMORI_DATABASE_CONNECTION:
            # Check if it's a valid PostgreSQL/SQLite connection string
            conn_str = settings.MEMORI_DATABASE_CONNECTION
            if conn_str.startswith(("postgresql://", "postgres://", "sqlite:///")):
                return conn_str
            else:
                logger.warning(
                    "memori_invalid_connection_string",
                    connection=conn_str,
                    falling_back_to_sqlite=True,
                )

        # Fallback to SQLite
        if settings.MEMORI_USE_SQLITE_FALLBACK:
            # Use SQLite in the same directory as ChromaDB
            sqlite_path = Path(settings.CHROMA_DB_PATH) / "memory.db"
            sqlite_path.parent.mkdir(parents=True, exist_ok=True)
            return f"sqlite:///{sqlite_path}"

        # Last resort: use default SQLite
        return "sqlite:///memory.db"

    def is_available(self) -> bool:
        """
        Check if Memori is available and initialized.

        Returns:
            True if Memori is available, False otherwise
        """
        return self._initialized and self.memori is not None

    def get_callbacks(self) -> List[Any]:
        """
        Get LangChain callbacks for Memori integration.

        Returns:
            List of callback handlers (empty if Memori not available)
        """
        if not self.is_available():
            return []

        # Memori integrates via its enable() method which intercepts LLM calls
        # For LangChain, we may need to use Memori's callback handlers if available
        # For now, return empty list as memori.enable() handles interception
        try:
            # If Memori has LangChain callbacks, return them here
            # Example: return [self.memori.get_langchain_callback()]
            return []
        except Exception as e:
            logger.warning("memori_callbacks_error", error=str(e))
            return []

    def get_conversation_history(
        self,
        session_id: str,
        limit: int = 10,
    ) -> List[Dict[str, str]]:
        """
        Get conversation history for a session.

        Args:
            session_id: Session identifier
            limit: Maximum number of messages to retrieve

        Returns:
            List of message dictionaries with 'role' and 'content'
        """
        if not self.is_available():
            return []

        try:
            # Memori stores conversations in the database
            # We need to query the database for conversation history
            # This is a placeholder - actual implementation depends on Memori's API
            # For now, return empty list as Memori handles history internally
            logger.debug("memori_get_history", session_id=session_id, limit=limit)
            return []
        except Exception as e:
            logger.error("memori_get_history_error", session_id=session_id, error=str(e))
            return []

    def store_message(
        self,
        session_id: str,
        role: str,
        content: str,
    ) -> None:
        """
        Store a message in conversation history.

        Args:
            session_id: Session identifier
            role: Message role ('user' or 'assistant')
            content: Message content
        """
        if not self.is_available():
            return

        try:
            # Memori automatically stores messages when LLM calls are made
            # This method is for manual storage if needed
            logger.debug("memori_store_message", session_id=session_id, role=role)
        except Exception as e:
            logger.error("memori_store_message_error", session_id=session_id, error=str(e))

    def clear_session(self, session_id: str) -> None:
        """
        Clear conversation history for a session.

        Args:
            session_id: Session identifier
        """
        if not self.is_available():
            return

        try:
            # Clear session history from Memori
            logger.info("memori_clear_session", session_id=session_id)
            # Implementation depends on Memori's API
        except Exception as e:
            logger.error("memori_clear_session_error", session_id=session_id, error=str(e))

