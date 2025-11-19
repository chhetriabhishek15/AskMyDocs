"""
ChromaDB repository for vector operations.
"""
from typing import List

import structlog

from app.vectorstore.chromadb_store import ChromaDBStore
from app.core.config import settings

logger = structlog.get_logger()


class ChromaDBRepository:
    """Repository for ChromaDB vector operations."""

    def __init__(self, chroma_store: ChromaDBStore):
        """
        Initialize ChromaDB repository.

        Args:
            chroma_store: ChromaDB store instance
        """
        self.chroma_store = chroma_store

    async def store_chunks(
        self,
        document_id: str,
        chunks: List,
    ) -> List[str]:
        """
        Store chunks in ChromaDB.

        Args:
            document_id: Document ID
            chunks: List of chunk objects (with text, markdown, metadata)

        Returns:
            List of chunk IDs
        """
        # Convert chunks to format expected by ChromaDB
        chunk_dicts = []
        for chunk in chunks:
            chunk_dict = {
                "text": chunk.text,
            }
            if hasattr(chunk, "markdown") and chunk.markdown:
                chunk_dict["markdown"] = chunk.markdown
            if hasattr(chunk, "metadata") and chunk.metadata:
                chunk_dict["metadata"] = chunk.metadata
            chunk_dicts.append(chunk_dict)

        # Add to ChromaDB
        chunk_ids = self.chroma_store.add_chunks(document_id, chunk_dicts)

        logger.info(
            "chunks_stored_in_chromadb",
            document_id=document_id,
            num_chunks=len(chunk_ids),
        )

        return chunk_ids

    async def search(
        self,
        query_text: str,
        top_k: int | None = None,
        document_id: str | None = None,
        min_score: float | None = None,
    ) -> List[dict]:
        """
        Search for similar chunks.

        Args:
            query_text: Query text
            top_k: Number of results to return
            document_id: Optional document ID to filter by
            min_score: Minimum similarity score (defaults to MIN_SIMILARITY_SCORE, None = no filtering)

        Returns:
            List of result dictionaries
        """
        top_k = top_k or settings.TOP_K_RETRIEVAL

        # Build filter if document_id provided
        filter_dict = None
        if document_id:
            filter_dict = {"document_id": document_id}

        # Search in ChromaDB
        results = self.chroma_store.search(
            query_text=query_text,
            n_results=top_k,
            filter_dict=filter_dict,
        )

        # Convert distance to similarity score
        # ChromaDB with cosine similarity returns distances in range [0, 2]
        # where 0 = identical, 2 = opposite
        # Convert to similarity: similarity = 1 - (distance / 2)
        for result in results:
            distance = result.get("distance", 1.0)
            # Cosine distance to similarity conversion
            similarity = max(0.0, min(1.0, 1.0 - (distance / 2.0)))
            result["similarity"] = similarity
            result["distance_raw"] = distance  # Keep raw distance for debugging

        # Log distances and similarities for debugging
        if results:
            distances = [r.get("distance", 0.0) for r in results]
            similarities = [r.get("similarity", 0.0) for r in results]
            logger.debug(
                "chromadb_similarity_conversion",
                distances=distances,
                similarities=similarities,
                min_distance=min(distances),
                max_distance=max(distances),
                min_similarity=min(similarities),
                max_similarity=max(similarities),
            )

        # Filter by minimum similarity if specified
        # If min_score is None, use default from config
        # If min_score is explicitly 0.0 or negative, don't filter
        if min_score is None:
            min_score = settings.MIN_SIMILARITY_SCORE
        
        if min_score > 0.0:
            filtered_results = [r for r in results if r.get("similarity", 0.0) >= min_score]
        else:
            filtered_results = results  # No filtering

        logger.debug(
            "chromadb_search_completed",
            top_k=top_k,
            results_before_filter=len(results),
            results_after_filter=len(filtered_results),
            min_score=min_score,
        )

        return filtered_results

    async def get_chunks_by_document(self, document_id: str) -> List[dict]:
        """
        Get all chunks for a document.

        Args:
            document_id: Document ID

        Returns:
            List of chunk dictionaries
        """
        return self.chroma_store.get_document_chunks(document_id)

    async def delete_chunks_by_document(self, document_id: str) -> int:
        """
        Delete all chunks for a document.

        Args:
            document_id: Document ID

        Returns:
            Number of deleted chunks (ChromaDB doesn't return exact count)
        """
        self.chroma_store.delete_document(document_id)
        return 0  # ChromaDB doesn't return count

    async def list_documents(self) -> List[dict]:
        """
        List all unique documents in ChromaDB.

        Returns:
            List of document dictionaries with id, filename, created_at, chunk_count
        """
        # Get all items from ChromaDB collection
        all_items = self.chroma_store.collection.get(
            include=['metadatas']
        )
        
        # Extract unique documents from metadata
        unique_documents = {}
        if all_items and all_items.get('metadatas'):
            for metadata in all_items['metadatas']:
                doc_id = metadata.get('document_id')
                if doc_id and doc_id not in unique_documents:
                    unique_documents[doc_id] = {
                        "id": doc_id,
                        "filename": metadata.get('filename', 'unknown'),
                        "created_at": metadata.get('created_at', 'unknown'),
                        "chunk_count": 0
                    }
        
        # Count chunks for each document
        for doc_id in unique_documents.keys():
            doc_chunks = await self.get_chunks_by_document(doc_id)
            unique_documents[doc_id]["chunk_count"] = len(doc_chunks)
        
        logger.info("documents_listed", num_documents=len(unique_documents))
        return list(unique_documents.values())

