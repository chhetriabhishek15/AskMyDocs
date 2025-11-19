"""
Chat endpoints.
"""
from fastapi import APIRouter, HTTPException
import structlog

from app.schemas.chat import ChatRequest, ChatResponse, SourceInfo
from app.rag.pipeline import RAGPipeline
from app.rag.retrieval import RetrievalService
from app.rag.memory_service import MemoryService
from app.services.llm_service import LLMService
from app.vectorstore.chromadb_store import ChromaDBStore
from app.repositories.chromadb_repository import ChromaDBRepository

logger = structlog.get_logger()
router = APIRouter()


def get_rag_pipeline() -> RAGPipeline:
    """
    Get or create RAG pipeline instance.

    Returns:
        RAGPipeline instance
    """
    # Initialize components
    chroma_store = ChromaDBStore()
    chroma_repository = ChromaDBRepository(chroma_store)
    retrieval_service = RetrievalService(chroma_repository)
    llm_service = LLMService()
    memory_service = MemoryService()

    # Create pipeline
    return RAGPipeline(
        retrieval_service=retrieval_service,
        llm_service=llm_service,
        memory_service=memory_service,
    )


@router.post("/chat", response_model=ChatResponse)
async def chat(request: ChatRequest):
    """
    Send a chat message and get AI response using RAG pipeline.

    Args:
        request: Chat request with query and session_id

    Returns:
        ChatResponse with answer, sources, and metadata

    Raises:
        HTTPException: If generation fails
    """
    try:
        logger.info(
            "chat_request_received",
            query_length=len(request.query),
            session_id=request.session_id,
        )

        # Get RAG pipeline
        pipeline = get_rag_pipeline()

        # Generate response
        rag_response = await pipeline.generate(
            query=request.query,
            session_id=request.session_id,
            top_k=request.top_k,
            min_score=request.min_score,
            document_id=request.document_id,
        )

        # Convert sources to response format
        sources = [
            SourceInfo(
                chunk_id=source.get("chunk_id", ""),
                document_id=source.get("document_id", ""),
                document_filename=source.get("document_filename", "unknown"),
                similarity_score=source.get("similarity_score", 0.0),
                preview=source.get("preview", source.get("text", "")[:200]),
            )
            for source in rag_response.sources
        ]

        response = ChatResponse(
            answer=rag_response.answer,
            sources=sources,
            session_id=rag_response.session_id,
            usage=rag_response.usage,
        )

        logger.info(
            "chat_response_sent",
            session_id=request.session_id,
            answer_length=len(rag_response.answer),
            num_sources=len(sources),
        )

        return response

    except ValueError as e:
        logger.error("chat_error", session_id=request.session_id, error=str(e))
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error("chat_unexpected_error", session_id=request.session_id, error=str(e), exc_info=True)
        raise HTTPException(status_code=500, detail="Internal server error during chat generation")
