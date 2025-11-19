"""
Ingestion service for end-to-end document processing.
"""
from pathlib import Path
from typing import Callable, Optional

import structlog

from app.services.document_parser import DocumentParserService, ParsedDocument
from app.services.chunking_service import ChunkingService
from app.repositories.chromadb_repository import ChromaDBRepository

logger = structlog.get_logger()


class IngestionService:
    """Service for processing documents end-to-end."""

    def __init__(
        self,
        document_parser: DocumentParserService,
        chunking_service: ChunkingService,
        chromadb_repository: ChromaDBRepository,
    ):
        """
        Initialize ingestion service.

        Args:
            document_parser: Document parser service
            chunking_service: Chunking service
            chromadb_repository: ChromaDB repository (handles embeddings internally)
        """
        self.document_parser = document_parser
        self.chunking_service = chunking_service
        self.chromadb_repository = chromadb_repository
        logger.info("ingestion_service_initialized")

    async def process_document(
        self,
        file_path: Path,
        filename: str,
        task_id: str | None = None,
        progress_callback: Optional[Callable[[float, str], None]] = None,
    ) -> str:
        """
        Process document end-to-end: parse → chunk → embed → store.

        Args:
            file_path: Path to document file
            filename: Original filename
            task_id: Optional task ID for tracking

        Returns:
            Document ID

        Raises:
            ValueError: If processing fails
        """
        try:
            logger.info(
                "document_processing_started",
                file_path=str(file_path),
                filename=filename,
                task_id=task_id,
            )

            # Step 1: Parse document
            logger.debug("step_1_parsing", task_id=task_id)
            if progress_callback:
                progress_callback(progress=0.4, message="Parsing document...")
            parsed_doc = await self.document_parser.parse_document(file_path)
            logger.info(
                "document_parsed",
                task_id=task_id,
                markdown_length=len(parsed_doc.markdown),
            )

            # Step 2: Generate document ID
            import uuid
            document_id = str(uuid.uuid4())
            logger.info("document_id_generated", task_id=task_id, document_id=document_id)

            # Step 3: Chunk document using HybridChunker with DoclingDocument
            logger.debug("step_3_chunking", task_id=task_id)
            if progress_callback:
                progress_callback(progress=0.6, message="Chunking document...")
            chunks = await self.chunking_service.chunk(
                docling_document=parsed_doc.docling_document,
                metadata={**parsed_doc.metadata, "filename": filename, "document_id": document_id},
                fallback_markdown=parsed_doc.markdown,  # Fallback if HybridChunker fails
            )
            logger.info("document_chunked", task_id=task_id, num_chunks=len(chunks))

            if not chunks:
                logger.warning("no_chunks_generated", task_id=task_id, document_id=document_id)
                return document_id

            # Step 4: Store chunks in ChromaDB (embeddings handled automatically)
            logger.debug("step_4_storing_chunks", task_id=task_id)
            if progress_callback:
                progress_callback(progress=0.8, message="Storing chunks in vector database...")
            await self.chromadb_repository.store_chunks(document_id, chunks)
            logger.info(
                "chunks_stored_in_chromadb",
                task_id=task_id,
                document_id=document_id,
                num_chunks=len(chunks),
            )

            logger.info(
                "document_processing_completed",
                task_id=task_id,
                document_id=str(document_id),
                num_chunks=len(chunks),
            )

            return document_id

        except Exception as e:
            logger.error(
                "document_processing_failed",
                task_id=task_id,
                file_path=str(file_path),
                filename=filename,
                error=str(e),
            )
            raise ValueError(f"Failed to process document: {e}") from e


