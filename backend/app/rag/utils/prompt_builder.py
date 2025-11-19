"""
Prompt builder utility for RAG pipeline.
"""
from typing import List, Dict, Any, Optional

from app.rag.prompts.templates import RAGPromptTemplate
from app.rag.utils.context_builder import ContextBuilder


class PromptBuilder:
    """Build prompts for RAG pipeline using templates and context."""

    def __init__(
        self,
        template_style: str = "default",
        include_history: bool = True,
    ):
        """
        Initialize prompt builder.

        Args:
            template_style: Prompt template style
            include_history: Whether to include conversation history
        """
        self.template = RAGPromptTemplate(
            system_prompt_style=template_style,
            include_conversation_history=include_history,
        )
        self.context_builder = ContextBuilder()

    def build_prompt(
        self,
        user_query: str,
        context_chunks: List[Dict[str, Any]],
        conversation_history: Optional[List[Dict[str, str]]] = None,
    ) -> str:
        """
        Build complete RAG prompt.

        Args:
            user_query: User's question
            context_chunks: Retrieved chunks
            conversation_history: Previous conversation messages

        Returns:
            Complete prompt string
        """
        return self.template.build(
            user_query=user_query,
            context_chunks=context_chunks,
            conversation_history=conversation_history,
        )

    def build_messages(
        self,
        user_query: str,
        context_chunks: List[Dict[str, Any]],
        conversation_history: Optional[List[Dict[str, str]]] = None,
    ) -> List[Dict[str, str]]:
        """
        Build messages list for LangChain.

        Args:
            user_query: User's question
            context_chunks: Retrieved chunks
            conversation_history: Previous messages

        Returns:
            List of message dictionaries
        """
        return self.template.build_messages(
            user_query=user_query,
            context_chunks=context_chunks,
            conversation_history=conversation_history,
        )

