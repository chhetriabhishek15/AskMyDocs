"""
Document endpoints.
"""
from fastapi import APIRouter, Query, HTTPException

import structlog

from app.schemas.retrieval import SearchRequest, SearchResponse
from app.vectorstore.chromadb_store import ChromaDBStore
from app.repositories.chromadb_repository import ChromaDBRepository
from app.rag.retrieval import RetrievalService

logger = structlog.get_logger()
router = APIRouter()


@router.get("/documents")
async def list_documents(
    page: int = Query(1, ge=1, description="Page number"),
    page_size: int = Query(20, ge=1, le=100, description="Items per page"),
):
    """
    List all ingested documents with pagination.

    Args:
        page: Page number (1-indexed)
        page_size: Number of items per page

    Returns:
        Document list response with pagination info
    """
    try:
        logger.info("documents_list_requested", page=page, page_size=page_size)

        # Initialize repository
        chroma_store = ChromaDBStore()
        chromadb_repository = ChromaDBRepository(chroma_store)

        # Get all documents
        all_documents = await chromadb_repository.list_documents()

        # Apply pagination
        total = len(all_documents)
        start_idx = (page - 1) * page_size
        end_idx = start_idx + page_size
        paginated_documents = all_documents[start_idx:end_idx]

        logger.info(
            "documents_list_completed",
            page=page,
            page_size=page_size,
            total=total,
            returned=len(paginated_documents),
        )

        return {
            "items": paginated_documents,
            "total": total,
            "page": page,
            "page_size": page_size,
        }

    except Exception as e:
        logger.error("documents_list_error", error=str(e), exc_info=True)
        raise HTTPException(status_code=500, detail=f"Failed to list documents: {str(e)}")


@router.get("/documents/{document_id}")
async def get_document(document_id: str):
    """
    Get details of a specific document.

    Returns:
        Document details
    """
    # TODO: Implement document retrieval
    return {"message": f"Get document {document_id} - to be implemented"}


@router.post("/documents/search", response_model=SearchResponse)
async def search_documents(request: SearchRequest):
    """
    Search documents using vector similarity.

    Args:
        request: Search request with query and optional filters

    Returns:
        Search results with retrieved chunks
    """
    try:
        logger.info("document_search_requested", query=request.query, top_k=request.top_k)

        # Initialize services
        chroma_store = ChromaDBStore()
        chromadb_repository = ChromaDBRepository(chroma_store)
        retrieval_service = RetrievalService(chromadb_repository)

        # Retrieve chunks
        formatted_results = await retrieval_service.retrieve_with_context(
            query_text=request.query,
            top_k=request.top_k,
            min_score=request.min_score,
            document_id=request.document_id,
            include_preview=True,
            preview_length=200,
        )

        # Convert to response format
        from app.schemas.retrieval import RetrievedChunkResponse

        results = [
            RetrievedChunkResponse(
                chunk_id=result["chunk_id"],
                document_id=result["document_id"],
                document_filename=result["document_filename"],
                text=result["text"],
                preview=result["preview"],
                similarity_score=result["similarity_score"],
                metadata=result.get("metadata", {}),
            )
            for result in formatted_results
        ]

        logger.info("document_search_completed", query=request.query, num_results=len(results))

        return SearchResponse(
            query=request.query,
            results=results,
            total=len(results),
        )

    except Exception as e:
        logger.error("document_search_error", query=request.query, error=str(e))
        raise
