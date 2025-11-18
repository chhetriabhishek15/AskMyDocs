"""
Conversation endpoints.
"""
from fastapi import APIRouter

router = APIRouter()


@router.get("/conversations/{session_id}")
async def get_conversation_history(session_id: str):
    """
    Get conversation history for a session.

    Returns:
        Conversation history
    """
    # TODO: Implement conversation history retrieval
    return {"message": f"Get conversation history for {session_id} - to be implemented"}


