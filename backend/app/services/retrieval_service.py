"""
Retrieval service for vector similarity search using ChromaDB.
"""
from typing import List, Dict, Any, Optional

import structlog

from app.repositories.chromadb_repository import ChromaDBRepository
from app.core.config import settings

logger = structlog.get_logger()


class RetrievedChunk:
    """Retrieved chunk with metadata."""

    def __init__(
        self,
        chunk_id: str,
        text: str,
        document_id: str,
        similarity_score: float,
        metadata: Dict[str, Any] | None = None,
    ):
        """
        Initialize retrieved chunk.

        Args:
            chunk_id: Chunk ID
            text: Chunk text content
            document_id: Document ID this chunk belongs to
            similarity_score: Similarity score (0.0 to 1.0)
            metadata: Additional metadata
        """
        self.chunk_id = chunk_id
        self.text = text
        self.document_id = document_id
        self.similarity_score = similarity_score
        self.metadata = metadata or {}

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "chunk_id": self.chunk_id,
            "text": self.text,
            "document_id": self.document_id,
            "similarity_score": self.similarity_score,
            "metadata": self.metadata,
        }


class RetrievalService:
    """Service for retrieving relevant chunks using vector similarity search."""

    def __init__(self, chromadb_repository: ChromaDBRepository):
        """
        Initialize retrieval service.

        Args:
            chromadb_repository: ChromaDB repository instance
        """
        self.chromadb_repository = chromadb_repository
        logger.info("retrieval_service_initialized")

    async def retrieve(
        self,
        query_text: str,
        top_k: int | None = None,
        min_score: float | None = None,
        document_id: str | None = None,
    ) -> List[RetrievedChunk]:
        """
        Retrieve relevant chunks for a query.

        Args:
            query_text: Query text to search for
            top_k: Number of results to return (defaults to TOP_K_RETRIEVAL)
            min_score: Minimum similarity score (defaults to MIN_SIMILARITY_SCORE)
            document_id: Optional document ID to filter search within a specific document

        Returns:
            List of RetrievedChunk objects sorted by similarity (highest first)
        """
        try:
            logger.info(
                "retrieval_started",
                query_length=len(query_text),
                top_k=top_k,
                document_id=document_id,
            )

            # Use defaults from config if not provided
            top_k = top_k or settings.TOP_K_RETRIEVAL
            if min_score is None:
                min_score = settings.MIN_SIMILARITY_SCORE

            # Search using ChromaDB repository
            # Pass min_score=None to let repository use config default, or pass explicit value
            results = await self.chromadb_repository.search(
                query_text=query_text,
                top_k=top_k,
                document_id=document_id,
                min_score=min_score,  # Pass min_score to repository
            )

            # Convert to RetrievedChunk objects
            # Repository already filters by min_score, so we can use all results
            retrieved_chunks = []
            for result in results:
                similarity = result.get("similarity", 0.0)

                chunk = RetrievedChunk(
                    chunk_id=result.get("id", ""),
                    text=result.get("text", ""),
                    document_id=result.get("metadata", {}).get("document_id", ""),
                    similarity_score=similarity,
                    metadata=result.get("metadata", {}),
                )
                retrieved_chunks.append(chunk)

            # Sort by similarity (highest first) - should already be sorted by ChromaDB
            retrieved_chunks.sort(key=lambda x: x.similarity_score, reverse=True)

            logger.info(
                "retrieval_completed",
                query_length=len(query_text),
                num_results=len(retrieved_chunks),
                top_similarity=retrieved_chunks[0].similarity_score if retrieved_chunks else 0.0,
            )

            return retrieved_chunks

        except Exception as e:
            logger.error("retrieval_error", query_text=query_text, error=str(e))
            raise ValueError(f"Failed to retrieve chunks: {e}") from e

    async def retrieve_with_context(
        self,
        query_text: str,
        top_k: int | None = None,
        min_score: float | None = None,
        document_id: str | None = None,
        include_preview: bool = True,
        preview_length: int = 200,
    ) -> List[Dict[str, Any]]:
        """
        Retrieve chunks with formatted context for RAG pipeline.

        Args:
            query_text: Query text to search for
            top_k: Number of results to return
            min_score: Minimum similarity score
            document_id: Optional document ID filter
            include_preview: Whether to include text preview
            preview_length: Length of preview text

        Returns:
            List of dictionaries with formatted chunk information
        """
        chunks = await self.retrieve(
            query_text=query_text,
            top_k=top_k,
            min_score=min_score,
            document_id=document_id,
        )

        # Format for RAG pipeline
        formatted_results = []
        for chunk in chunks:
            preview = chunk.text[:preview_length] + "..." if len(chunk.text) > preview_length else chunk.text
            
            formatted = {
                "chunk_id": chunk.chunk_id,
                "document_id": chunk.document_id,
                "document_filename": chunk.metadata.get("filename", "unknown"),
                "text": chunk.text,
                "similarity_score": chunk.similarity_score,
                "metadata": chunk.metadata,
            }
            
            if include_preview:
                formatted["preview"] = preview

            formatted_results.append(formatted)

        return formatted_results

    async def get_chunks_for_document(
        self,
        document_id: str,
    ) -> List[RetrievedChunk]:
        """
        Get all chunks for a specific document (non-semantic search).

        Args:
            document_id: Document ID

        Returns:
            List of RetrievedChunk objects
        """
        try:
            logger.info("retrieving_document_chunks", document_id=document_id)

            # Get chunks from repository
            chunks_data = await self.chromadb_repository.get_chunks_by_document(document_id)

            # Convert to RetrievedChunk objects
            retrieved_chunks = []
            for chunk_data in chunks_data:
                chunk = RetrievedChunk(
                    chunk_id=chunk_data.get("id", ""),
                    text=chunk_data.get("text", ""),
                    document_id=document_id,
                    similarity_score=1.0,  # Not a similarity search, so score is 1.0
                    metadata=chunk_data.get("metadata", {}),
                )
                retrieved_chunks.append(chunk)

            logger.info(
                "document_chunks_retrieved",
                document_id=document_id,
                num_chunks=len(retrieved_chunks),
            )

            return retrieved_chunks

        except Exception as e:
            logger.error("get_document_chunks_error", document_id=document_id, error=str(e))
            raise ValueError(f"Failed to get chunks for document: {e}") from e

