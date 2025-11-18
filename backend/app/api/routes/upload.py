"""
File upload endpoints.
"""
from fastapi import APIRouter

router = APIRouter()


@router.post("/upload")
async def upload_file():
    """
    Upload a document for ingestion.

    Returns:
        Task ID and status
    """
    # TODO: Implement file upload
    return {"message": "Upload endpoint - to be implemented"}


