"""
Document endpoints.
"""
from fastapi import APIRouter

router = APIRouter()


@router.get("/documents")
async def list_documents():
    """
    List all ingested documents.

    Returns:
        List of documents
    """
    # TODO: Implement document listing
    return {"message": "Documents endpoint - to be implemented"}


@router.get("/documents/{document_id}")
async def get_document(document_id: str):
    """
    Get details of a specific document.

    Returns:
        Document details
    """
    # TODO: Implement document retrieval
    return {"message": f"Get document {document_id} - to be implemented"}
