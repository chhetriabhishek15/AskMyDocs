"""
Chat endpoints.
"""
from fastapi import APIRouter

router = APIRouter()


@router.post("/chat")
async def chat():
    """
    Send a chat message and get AI response.

    Returns:
        AI response with sources
    """
    # TODO: Implement chat endpoint
    return {"message": "Chat endpoint - to be implemented"}


