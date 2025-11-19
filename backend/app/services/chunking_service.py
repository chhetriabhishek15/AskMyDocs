"""
Chunking service using Docling's HybridChunker.
"""
from typing import List, Dict, Any

import structlog

from app.core.config import settings

logger = structlog.get_logger()


class Chunk:
    """Chunk data structure."""

    def __init__(
        self,
        text: str,
        markdown: str | None = None,
        metadata: Dict[str, Any] | None = None,
    ):
        """
        Initialize chunk.

        Args:
            text: Chunk text content
            markdown: Chunk markdown content (optional)
            metadata: Chunk metadata
        """
        self.text = text
        self.markdown = markdown or text
        self.metadata = metadata or {}


class ChunkingService:
    """Service for chunking documents using Docling's HybridChunker."""

    def __init__(
        self,
        max_tokens: int | None = None,
        tokenizer_model: str | None = None,
        merge_peers: bool = True,
    ):
        """
        Initialize chunking service.

        Args:
            max_tokens: Maximum tokens per chunk (defaults to CHUNK_SIZE)
            tokenizer_model: Tokenizer model ID (defaults to sentence-transformers/all-MiniLM-L6-v2)
            merge_peers: Whether to merge small adjacent chunks
        """
        self.max_tokens = max_tokens or settings.CHUNK_SIZE
        self.tokenizer_model = tokenizer_model or settings.CHUNKER_TOKENIZER_MODEL
        self.merge_peers = merge_peers if merge_peers is not None else settings.CHUNKER_MERGE_PEERS
        self._tokenizer = None
        self._chunker = None
        logger.info(
            "chunking_service_initialized",
            max_tokens=self.max_tokens,
            tokenizer_model=self.tokenizer_model,
            merge_peers=self.merge_peers,
        )

    def _get_tokenizer(self):
        """Lazy load tokenizer."""
        if self._tokenizer is None:
            try:
                from transformers import AutoTokenizer
                logger.info("loading_tokenizer", model=self.tokenizer_model)
                self._tokenizer = AutoTokenizer.from_pretrained(self.tokenizer_model)
            except ImportError:
                logger.error("transformers_not_available")
                raise ImportError("transformers library is required for HybridChunker")
        return self._tokenizer

    def _get_chunker(self):
        """Lazy load HybridChunker."""
        if self._chunker is None:
            try:
                from docling.chunking import HybridChunker
                tokenizer = self._get_tokenizer()
                logger.info("creating_hybrid_chunker", max_tokens=self.max_tokens)
                self._chunker = HybridChunker(
                    tokenizer=tokenizer,
                    max_tokens=self.max_tokens,
                    merge_peers=self.merge_peers,
                )
            except ImportError:
                logger.error("hybrid_chunker_not_available")
                raise ImportError("docling.chunking.HybridChunker is required")
        return self._chunker

    async def chunk(
        self,
        docling_document: Any,
        metadata: Dict[str, Any] | None = None,
        fallback_markdown: str | None = None,
    ) -> List[Chunk]:
        """
        Chunk DoclingDocument using HybridChunker.

        Args:
            docling_document: DoclingDocument object from document parser
            metadata: Document metadata
            fallback_markdown: Fallback markdown if HybridChunker fails

        Returns:
            List of chunks
        """
        try:
            logger.info("chunking_document_with_hybrid_chunker")

            # If no DoclingDocument provided, use fallback
            if docling_document is None:
                if fallback_markdown:
                    logger.warning("no_docling_document_provided", using_fallback=True)
                    return self._simple_chunk(fallback_markdown, metadata)
                else:
                    raise ValueError("docling_document is required for HybridChunker")

            # Get chunker
            chunker = self._get_chunker()

            # Chunk the DoclingDocument
            logger.debug("calling_hybrid_chunker_chunk")
            chunk_iter = chunker.chunk(dl_doc=docling_document)
            chunks = list(chunk_iter)

            logger.info("hybrid_chunker_completed", num_chunks=len(chunks))

            # Convert to our Chunk objects
            result = []
            tokenizer = self._get_tokenizer()
            
            for i, chunk in enumerate(chunks):
                # Get chunk text
                chunk_text = chunk.text if hasattr(chunk, "text") else str(chunk)
                
                # Use contextualize to preserve headings and metadata
                try:
                    contextualized_text = chunker.contextualize(chunk=chunk)
                except Exception as e:
                    logger.warning("contextualize_failed", chunk_index=i, error=str(e))
                    contextualized_text = chunk_text

                # Count tokens for metadata
                try:
                    tokens = tokenizer.encode(chunk_text)
                    token_count = len(tokens)
                except Exception:
                    token_count = len(chunk_text.split())  # Fallback to word count

                chunk_obj = Chunk(
                    text=contextualized_text,  # Use contextualized text for better context
                    markdown=contextualized_text,
                    metadata={
                        "chunk_index": i,
                        "chunk_size": len(chunk_text),
                        "token_count": token_count,
                        "method": "hybrid_chunker",
                        **(metadata or {}),
                    },
                )
                result.append(chunk_obj)

            logger.info("document_chunked", num_chunks=len(result))
            return result

        except ImportError as e:
            logger.error("chunking_import_error", error=str(e))
            if fallback_markdown:
                logger.warning("using_fallback_chunking")
                return self._simple_chunk(fallback_markdown, metadata)
            raise
        except Exception as e:
            logger.error("chunking_error", error=str(e), exc_info=True)
            # Fallback to simple chunking if available
            if fallback_markdown:
                logger.warning("using_fallback_chunking_after_error")
                return self._simple_chunk(fallback_markdown, metadata)
            raise ValueError(f"Failed to chunk document: {e}") from e

    def _simple_chunk(self, markdown: str, metadata: Dict[str, Any] | None = None) -> List[Chunk]:
        """
        Simple fallback chunking strategy.

        Args:
            markdown: Document markdown content
            metadata: Document metadata

        Returns:
            List of chunks
        """
        logger.info("using_simple_chunking")
        # Simple sentence-based chunking
        import re

        # Split by paragraphs first
        paragraphs = re.split(r"\n\s*\n", markdown)
        chunks = []
        current_chunk = ""
        chunk_index = 0

        # Use max_tokens as character limit approximation (rough estimate: 1 token ≈ 4 chars)
        max_chars = self.max_tokens * 4

        for para in paragraphs:
            para = para.strip()
            if not para:
                continue

            # If adding this paragraph would exceed max size, save current chunk
            if len(current_chunk) + len(para) > max_chars and current_chunk:
                chunks.append(
                    Chunk(
                        text=current_chunk,
                        markdown=current_chunk,
                        metadata={
                            "chunk_index": chunk_index,
                            "chunk_size": len(current_chunk),
                            "method": "simple",
                            **(metadata or {}),
                        },
                    )
                )
                current_chunk = para
                chunk_index += 1
            else:
                current_chunk += "\n\n" + para if current_chunk else para

        # Add final chunk
        if current_chunk:
            chunks.append(
                Chunk(
                    text=current_chunk,
                    markdown=current_chunk,
                    metadata={
                        "chunk_index": chunk_index,
                        "chunk_size": len(current_chunk),
                        "method": "simple",
                        **(metadata or {}),
                    },
                )
            )

        return chunks


