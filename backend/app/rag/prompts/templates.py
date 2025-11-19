"""
RAG prompt templates.
"""
from typing import List, Dict, Any, Optional

from app.rag.prompts.system_prompts import get_system_prompt


class RAGPromptTemplate:
    """Template for building RAG prompts."""

    def __init__(
        self,
        system_prompt_style: str = "default",
        include_conversation_history: bool = True,
        max_history_messages: int = 5,
    ):
        """
        Initialize RAG prompt template.

        Args:
            system_prompt_style: Style of system prompt ("default", "concise", "detailed")
            include_conversation_history: Whether to include conversation history
            max_history_messages: Maximum number of history messages to include
        """
        self.system_prompt_style = system_prompt_style
        self.include_conversation_history = include_conversation_history
        self.max_history_messages = max_history_messages

    def build(
        self,
        user_query: str,
        context_chunks: List[Dict[str, Any]],
        conversation_history: Optional[List[Dict[str, str]]] = None,
    ) -> str:
        """
        Build RAG prompt from components.

        Args:
            user_query: User's question
            context_chunks: Retrieved chunks with text and metadata
            conversation_history: Previous conversation messages (list of {"role": "user"/"assistant", "content": "..."})

        Returns:
            Formatted prompt string
        """
        # Get system prompt
        system_prompt = get_system_prompt(self.system_prompt_style)

        # Build context section
        context_section = self._build_context_section(context_chunks)

        # Build conversation history section if enabled
        history_section = ""
        if self.include_conversation_history and conversation_history:
            history_section = self._build_history_section(conversation_history)

        # Build final prompt
        prompt_parts = [system_prompt]

        if context_section:
            prompt_parts.append(context_section)

        if history_section:
            prompt_parts.append(history_section)

        prompt_parts.append(f"## User Question:\n{user_query}")
        prompt_parts.append("\n## Your Response:")

        return "\n\n".join(prompt_parts)

    def _build_context_section(self, context_chunks: List[Dict[str, Any]]) -> str:
        """
        Build context section from retrieved chunks.

        Args:
            context_chunks: List of chunk dictionaries

        Returns:
            Formatted context section
        """
        if not context_chunks:
            return "## Context Documents:\n\nNo relevant context found."

        context_lines = ["## Context Documents:\n"]
        
        for i, chunk in enumerate(context_chunks, 1):
            chunk_text = chunk.get("text", "")
            document_name = chunk.get("document_filename", chunk.get("metadata", {}).get("filename", "Unknown"))
            similarity = chunk.get("similarity_score", 0.0)
            
            context_lines.append(f"### Document {i}: {document_name} (Relevance: {similarity:.2f})")
            context_lines.append(chunk_text)
            context_lines.append("")  # Empty line between chunks

        return "\n".join(context_lines)

    def _build_history_section(
        self,
        conversation_history: List[Dict[str, str]],
    ) -> str:
        """
        Build conversation history section.

        Args:
            conversation_history: List of message dictionaries

        Returns:
            Formatted history section
        """
        if not conversation_history:
            return ""

        # Take last N messages
        recent_messages = conversation_history[-self.max_history_messages:]

        history_lines = ["## Previous Conversation:\n"]
        
        for msg in recent_messages:
            role = msg.get("role", "user")
            content = msg.get("content", "")
            
            # Format role name
            role_name = "User" if role == "user" else "Assistant"
            history_lines.append(f"{role_name}: {content}")

        history_lines.append("")  # Empty line at end
        return "\n".join(history_lines)

    def build_messages(
        self,
        user_query: str,
        context_chunks: List[Dict[str, Any]],
        conversation_history: Optional[List[Dict[str, str]]] = None,
    ) -> List[Dict[str, str]]:
        """
        Build messages list for LangChain (alternative format).

        Args:
            user_query: User's question
            context_chunks: Retrieved chunks
            conversation_history: Previous messages

        Returns:
            List of message dictionaries for LangChain
        """
        # Get system prompt
        system_prompt = get_system_prompt(self.system_prompt_style)

        # Build context
        context_section = self._build_context_section(context_chunks)

        # Combine system prompt and context
        full_system_content = f"{system_prompt}\n\n{context_section}"

        messages = [
            {"role": "system", "content": full_system_content},
        ]

        # Add conversation history
        if self.include_conversation_history and conversation_history:
            for msg in conversation_history[-self.max_history_messages:]:
                messages.append({
                    "role": msg.get("role", "user"),
                    "content": msg.get("content", ""),
                })

        # Add current user query
        messages.append({"role": "user", "content": user_query})

        return messages

