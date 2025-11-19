"""
Context builder for formatting retrieved chunks into context strings.
"""
from typing import List, Dict, Any

import structlog

logger = structlog.get_logger()


class ContextBuilder:
    """Build context strings from retrieved chunks."""

    def __init__(
        self,
        include_metadata: bool = True,
        include_similarity: bool = True,
        max_chunk_length: int | None = None,
    ):
        """
        Initialize context builder.

        Args:
            include_metadata: Whether to include document metadata
            include_similarity: Whether to include similarity scores
            max_chunk_length: Maximum length per chunk (None = no limit)
        """
        self.include_metadata = include_metadata
        self.include_similarity = include_similarity
        self.max_chunk_length = max_chunk_length

    def build_context(
        self,
        chunks: List[Dict[str, Any]],
        deduplicate: bool = True,
    ) -> str:
        """
        Build context string from retrieved chunks.

        Args:
            chunks: List of chunk dictionaries with text, metadata, similarity_score
            deduplicate: Whether to remove duplicate chunks (by text)

        Returns:
            Formatted context string
        """
        if not chunks:
            return "No relevant context found."

        # Deduplicate if requested
        if deduplicate:
            chunks = self._deduplicate_chunks(chunks)

        context_parts = []
        for i, chunk in enumerate(chunks, 1):
            chunk_text = chunk.get("text", "")
            
            # Truncate if needed
            if self.max_chunk_length and len(chunk_text) > self.max_chunk_length:
                chunk_text = chunk_text[:self.max_chunk_length] + "..."

            # Build chunk header
            header_parts = [f"### Chunk {i}"]
            
            if self.include_metadata:
                doc_name = chunk.get("document_filename") or chunk.get("metadata", {}).get("filename", "Unknown")
                header_parts.append(f"from {doc_name}")
            
            if self.include_similarity:
                similarity = chunk.get("similarity_score", 0.0)
                header_parts.append(f"(Relevance: {similarity:.2f})")

            context_parts.append(" ".join(header_parts))
            context_parts.append(chunk_text)
            context_parts.append("")  # Empty line between chunks

        return "\n".join(context_parts)

    def _deduplicate_chunks(
        self,
        chunks: List[Dict[str, Any]],
    ) -> List[Dict[str, Any]]:
        """
        Remove duplicate chunks based on text content.

        Args:
            chunks: List of chunk dictionaries

        Returns:
            Deduplicated list of chunks
        """
        seen_texts = set()
        unique_chunks = []

        for chunk in chunks:
            chunk_text = chunk.get("text", "").strip()
            if chunk_text and chunk_text not in seen_texts:
                seen_texts.add(chunk_text)
                unique_chunks.append(chunk)

        if len(unique_chunks) < len(chunks):
            logger.debug(
                "chunks_deduplicated",
                original_count=len(chunks),
                unique_count=len(unique_chunks),
            )

        return unique_chunks

    def build_context_summary(
        self,
        chunks: List[Dict[str, Any]],
    ) -> Dict[str, Any]:
        """
        Build summary of context chunks.

        Args:
            chunks: List of chunk dictionaries

        Returns:
            Summary dictionary with counts, document names, etc.
        """
        if not chunks:
            return {
                "total_chunks": 0,
                "documents": [],
                "total_text_length": 0,
            }

        # Get unique documents
        documents = set()
        total_length = 0

        for chunk in chunks:
            doc_name = chunk.get("document_filename") or chunk.get("metadata", {}).get("filename", "Unknown")
            documents.add(doc_name)
            total_length += len(chunk.get("text", ""))

        return {
            "total_chunks": len(chunks),
            "documents": sorted(list(documents)),
            "total_text_length": total_length,
            "average_similarity": sum(c.get("similarity_score", 0.0) for c in chunks) / len(chunks) if chunks else 0.0,
        }

