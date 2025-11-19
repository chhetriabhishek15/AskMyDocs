"""
Document parsing service using docling-core.
"""
from pathlib import Path
from typing import Dict, Any

import structlog

logger = structlog.get_logger()


class ParsedDocument:
    """Parsed document data structure."""

    def __init__(
        self,
        markdown: str,
        metadata: Dict[str, Any],
        docling_document: Any = None,  # DoclingDocument object for chunking
        structure: Dict[str, Any] | None = None,
    ):
        """
        Initialize parsed document.

        Args:
            markdown: Document content as markdown
            metadata: Document metadata
            docling_document: DoclingDocument object (for HybridChunker)
            structure: Document structure (optional)
        """
        self.markdown = markdown
        self.metadata = metadata
        self.docling_document = docling_document
        self.structure = structure or {}


class DocumentParserService:
    """Service for parsing documents using docling."""

    def __init__(self):
        """Initialize document parser service."""
        logger.info("document_parser_service_initialized")

    async def parse_document(self, file_path: Path) -> ParsedDocument:
        """
        Parse document using docling.

        Args:
            file_path: Path to document file

        Returns:
            ParsedDocument with markdown and metadata

        Raises:
            ValueError: If document cannot be parsed
        """
        try:
            logger.info("parsing_document", file_path=str(file_path))

            # Import docling components
            from docling.document_converter import DocumentConverter

            # Create converter
            converter = DocumentConverter()

            # Convert document
            result = converter.convert(str(file_path))

            # Get DoclingDocument object
            docling_doc = result.document if hasattr(result, "document") else result

            # Extract markdown
            if hasattr(docling_doc, "export_to_markdown"):
                markdown = docling_doc.export_to_markdown()
            else:
                # Fallback: convert to string if markdown export not available
                markdown = str(docling_doc)

            # Extract metadata
            metadata = {
                "file_path": str(file_path),
                "file_name": file_path.name,
                "file_size": file_path.stat().st_size,
                "document_type": docling_doc.doctype if hasattr(docling_doc, "doctype") else "unknown",
            }

            # Extract structure if available
            structure = {}
            if hasattr(docling_doc, "structure"):
                structure = docling_doc.structure

            logger.info(
                "document_parsed",
                file_path=str(file_path),
                markdown_length=len(markdown),
                metadata=metadata,
            )

            return ParsedDocument(
                markdown=markdown,
                metadata=metadata,
                docling_document=docling_doc,
                structure=structure,
            )

        except ImportError as e:
            logger.error("docling_core_import_error", error=str(e))
            raise ValueError(f"Failed to import docling-core: {e}")
        except Exception as e:
            logger.error("document_parse_error", file_path=str(file_path), error=str(e))
            raise ValueError(f"Failed to parse document: {e}")

