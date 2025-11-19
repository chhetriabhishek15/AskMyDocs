"""
RAG pipeline orchestrating retrieval, memory, prompt building, and LLM generation.
"""
from typing import List, Dict, Any, Optional

import structlog

from app.rag.retrieval import RetrievalService
from app.rag.memory_service import MemoryService
from app.rag.prompts.templates import RAGPromptTemplate
from app.rag.utils.context_builder import ContextBuilder
from app.services.llm_service import LLMService
from app.core.config import settings

logger = structlog.get_logger()


class RAGResponse:
    """Response from RAG pipeline."""

    def __init__(
        self,
        answer: str,
        sources: List[Dict[str, Any]],
        session_id: str,
        usage: Dict[str, Any] | None = None,
    ):
        """
        Initialize RAG response.

        Args:
            answer: Generated answer text
            sources: List of source chunks used
            session_id: Session identifier
            usage: Token usage information
        """
        self.answer = answer
        self.sources = sources
        self.session_id = session_id
        self.usage = usage or {}

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "answer": self.answer,
            "sources": [
                {
                    "chunk_id": s.get("chunk_id"),
                    "document_id": s.get("document_id"),
                    "document_filename": s.get("document_filename"),
                    "similarity_score": s.get("similarity_score"),
                    "preview": s.get("preview", s.get("text", "")[:200]),
                }
                for s in self.sources
            ],
            "session_id": self.session_id,
            "usage": self.usage,
        }


class RAGPipeline:
    """Main RAG pipeline orchestrating all components."""

    def __init__(
        self,
        retrieval_service: RetrievalService,
        llm_service: LLMService,
        memory_service: MemoryService | None = None,
        prompt_template: RAGPromptTemplate | None = None,
    ):
        """
        Initialize RAG pipeline.

        Args:
            retrieval_service: Service for retrieving relevant chunks
            llm_service: Service for LLM generation
            memory_service: Optional service for conversation memory
            prompt_template: Optional prompt template (defaults to standard template)
        """
        self.retrieval_service = retrieval_service
        self.llm_service = llm_service
        self.memory_service = memory_service or MemoryService()
        self.prompt_template = prompt_template or RAGPromptTemplate()
        self.context_builder = ContextBuilder()

        logger.info(
            "rag_pipeline_initialized",
            memory_available=self.memory_service.is_available(),
        )

    async def generate(
        self,
        query: str,
        session_id: str,
        top_k: int | None = None,
        min_score: float | None = None,
        document_id: str | None = None,
    ) -> RAGResponse:
        """
        Generate response using RAG pipeline.

        Args:
            query: User's question
            session_id: Session identifier for memory
            top_k: Number of chunks to retrieve
            min_score: Minimum similarity score for chunks
            document_id: Optional document ID to filter search

        Returns:
            RAGResponse with answer and sources

        Raises:
            ValueError: If generation fails
        """
        try:
            logger.info(
                "rag_pipeline_started",
                query_length=len(query),
                session_id=session_id,
                top_k=top_k,
            )

            # Step 1: Retrieve relevant chunks
            context_chunks = await self.retrieval_service.retrieve_with_context(
                query_text=query,
                top_k=top_k,
                min_score=min_score,
                document_id=document_id,
            )

            logger.debug(
                "rag_retrieval_completed",
                num_chunks=len(context_chunks),
                session_id=session_id,
            )

            # Step 2: Get conversation history from memory (if available)
            conversation_history = []
            if self.memory_service.is_available():
                conversation_history = self.memory_service.get_conversation_history(
                    session_id=session_id,
                    limit=5,
                )

            # Step 3: Build prompt using template
            prompt = self.prompt_template.build(
                user_query=query,
                context_chunks=context_chunks,
                conversation_history=conversation_history,
            )

            # Step 4: Get Memori callbacks if available
            callbacks = []
            if self.memory_service.is_available():
                callbacks = self.memory_service.get_callbacks()

            # Step 5: Generate response using LLM
            llm_response = await self.llm_service.generate(
                prompt=prompt,
                use_cache=True,
                callbacks=callbacks,
            )

            # Step 6: Store conversation in memory (if available)
            if self.memory_service.is_available():
                self.memory_service.store_message(
                    session_id=session_id,
                    role="user",
                    content=query,
                )
                self.memory_service.store_message(
                    session_id=session_id,
                    role="assistant",
                    content=llm_response.text,
                )

            # Step 7: Build response
            response = RAGResponse(
                answer=llm_response.text,
                sources=context_chunks,
                session_id=session_id,
                usage=llm_response.usage,
            )

            logger.info(
                "rag_pipeline_completed",
                session_id=session_id,
                answer_length=len(llm_response.text),
                num_sources=len(context_chunks),
            )

            return response

        except Exception as e:
            logger.error(
                "rag_pipeline_error",
                query=query,
                session_id=session_id,
                error=str(e),
            )
            raise ValueError(f"RAG pipeline failed: {e}") from e

    async def generate_from_messages(
        self,
        messages: List[Dict[str, str]],
        session_id: str,
        top_k: int | None = None,
        min_score: float | None = None,
        document_id: str | None = None,
    ) -> RAGResponse:
        """
        Generate response from conversation messages.

        Args:
            messages: List of message dictionaries with 'role' and 'content'
            session_id: Session identifier
            top_k: Number of chunks to retrieve
            min_score: Minimum similarity score
            document_id: Optional document ID filter

        Returns:
            RAGResponse object
        """
        # Extract the last user message as the query
        user_messages = [msg for msg in messages if msg.get("role") == "user"]
        if not user_messages:
            raise ValueError("No user message found in messages")

        query = user_messages[-1]["content"]

        # Get conversation history (all messages except the last user message)
        conversation_history = messages[:-1] if len(messages) > 1 else []

        try:
            logger.info(
                "rag_pipeline_from_messages_started",
                query_length=len(query),
                session_id=session_id,
                num_messages=len(messages),
            )

            # Step 1: Retrieve relevant chunks
            context_chunks = await self.retrieval_service.retrieve_with_context(
                query_text=query,
                top_k=top_k,
                min_score=min_score,
                document_id=document_id,
            )

            # Step 2: Build prompt
            prompt = self.prompt_template.build(
                user_query=query,
                context_chunks=context_chunks,
                conversation_history=conversation_history,
            )

            # Step 3: Get callbacks
            callbacks = []
            if self.memory_service.is_available():
                callbacks = self.memory_service.get_callbacks()

            # Step 4: Generate response
            llm_response = await self.llm_service.generate(
                prompt=prompt,
                use_cache=True,
                callbacks=callbacks,
            )

            # Step 5: Store in memory
            if self.memory_service.is_available():
                for msg in messages:
                    self.memory_service.store_message(
                        session_id=session_id,
                        role=msg.get("role", "user"),
                        content=msg.get("content", ""),
                    )
                self.memory_service.store_message(
                    session_id=session_id,
                    role="assistant",
                    content=llm_response.text,
                )

            # Step 6: Build response
            response = RAGResponse(
                answer=llm_response.text,
                sources=context_chunks,
                session_id=session_id,
                usage=llm_response.usage,
            )

            logger.info(
                "rag_pipeline_from_messages_completed",
                session_id=session_id,
                answer_length=len(llm_response.text),
            )

            return response

        except Exception as e:
            logger.error(
                "rag_pipeline_from_messages_error",
                session_id=session_id,
                error=str(e),
            )
            raise ValueError(f"RAG pipeline failed: {e}") from e

