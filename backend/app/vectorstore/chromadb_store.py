"""
ChromaDB vector store for document and chunk storage.
"""
import os
from pathlib import Path
from typing import List, Dict, Any, Optional
from uuid import UUID
import chromadb
from chromadb.config import Settings as ChromaSettings

import structlog

from app.core.config import settings

logger = structlog.get_logger()


class ChromaDBStore:
    """ChromaDB vector store for document storage and retrieval."""

    def __init__(self, persist_directory: str | None = None, collection_name: str | None = None):
        """
        Initialize ChromaDB store.

        Args:
            persist_directory: Directory for persistent storage
            collection_name: Name of the collection
        """
        self.persist_directory = persist_directory or settings.CHROMA_DB_PATH
        self.collection_name = collection_name or settings.CHROMA_COLLECTION_NAME

        # Ensure directory exists
        Path(self.persist_directory).mkdir(parents=True, exist_ok=True)

        # Initialize ChromaDB client with persistence
        self.client = chromadb.PersistentClient(
            path=self.persist_directory,
            settings=ChromaSettings(
                anonymized_telemetry=False,
                allow_reset=True,
            ),
        )

        # Get or create collection
        # ChromaDB handles embeddings internally
        embedding_function = None
        if settings.CHROMA_EMBEDDING_FUNCTION:
            # Can specify custom embedding function if needed
            # For now, use default
            pass

        self.collection = self.client.get_or_create_collection(
            name=self.collection_name,
            embedding_function=embedding_function,  # None = use default
            metadata={"hnsw:space": "cosine"},  # Use cosine similarity
        )

        logger.info(
            "chromadb_initialized",
            persist_directory=self.persist_directory,
            collection_name=self.collection_name,
        )

    def add_chunks(
        self,
        document_id: str,
        chunks: List[Dict[str, Any]],
        metadatas: List[Dict[str, Any]] | None = None,
    ) -> List[str]:
        """
        Add chunks to ChromaDB.

        Args:
            document_id: Document ID
            chunks: List of chunk dictionaries with 'text' and optionally 'markdown'
            metadatas: List of metadata dictionaries (one per chunk)

        Returns:
            List of chunk IDs
        """
        if not chunks:
            return []

        # Prepare data for ChromaDB
        texts = [chunk.get("text", chunk.get("markdown", str(chunk))) for chunk in chunks]
        ids = [f"{document_id}_{i}" for i in range(len(chunks))]

        # Prepare metadatas
        if metadatas is None:
            metadatas = []
            for i, chunk in enumerate(chunks):
                metadata = {
                    "document_id": document_id,
                    "chunk_index": i,
                    **(chunk.get("metadata", {})),
                }
                if "markdown" in chunk:
                    metadata["markdown"] = chunk["markdown"]
                metadatas.append(metadata)
        else:
            # Add document_id to each metadata
            for i, metadata in enumerate(metadatas):
                metadata["document_id"] = document_id
                metadata["chunk_index"] = i

        # Add to collection
        self.collection.add(
            ids=ids,
            documents=texts,
            metadatas=metadatas,
        )

        logger.info(
            "chunks_added_to_chromadb",
            document_id=document_id,
            num_chunks=len(chunks),
        )

        return ids

    def search(
        self,
        query_text: str,
        n_results: int = 5,
        filter_dict: Dict[str, Any] | None = None,
    ) -> List[Dict[str, Any]]:
        """
        Search for similar chunks.

        Args:
            query_text: Query text
            n_results: Number of results to return
            filter_dict: Optional filter dictionary (e.g., {"document_id": "..."})

        Returns:
            List of result dictionaries with 'text', 'metadata', 'distance', 'id'
        """
        # Build where clause for filtering
        where = filter_dict if filter_dict else None

        # Search
        results = self.collection.query(
            query_texts=[query_text],
            n_results=n_results,
            where=where,
        )

        # Format results
        formatted_results = []
        if results["ids"] and len(results["ids"]) > 0:
            for i in range(len(results["ids"][0])):
                formatted_results.append(
                    {
                        "id": results["ids"][0][i],
                        "text": results["documents"][0][i] if results["documents"] else "",
                        "metadata": results["metadatas"][0][i] if results["metadatas"] else {},
                        "distance": results["distances"][0][i] if results["distances"] else 0.0,
                    }
                )

        logger.debug(
            "chromadb_search_completed",
            query_length=len(query_text),
            n_results=n_results,
            results_count=len(formatted_results),
        )

        return formatted_results

    def delete_document(self, document_id: str) -> int:
        """
        Delete all chunks for a document.

        Args:
            document_id: Document ID

        Returns:
            Number of deleted chunks
        """
        # Delete chunks with matching document_id
        self.collection.delete(
            where={"document_id": document_id},
        )

        logger.info("document_deleted_from_chromadb", document_id=document_id)
        return 0  # ChromaDB doesn't return count, but we log it

    def get_document_chunks(self, document_id: str) -> List[Dict[str, Any]]:
        """
        Get all chunks for a document.

        Args:
            document_id: Document ID

        Returns:
            List of chunk dictionaries
        """
        # Query with filter
        results = self.collection.get(
            where={"document_id": document_id},
        )

        # Format results
        chunks = []
        if results["ids"]:
            for i in range(len(results["ids"])):
                chunks.append(
                    {
                        "id": results["ids"][i],
                        "text": results["documents"][i] if results["documents"] else "",
                        "metadata": results["metadatas"][i] if results["metadatas"] else {},
                    }
                )

        return chunks

