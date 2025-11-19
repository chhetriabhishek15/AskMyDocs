"""
Prompt templates package.
"""
from app.rag.prompts.templates import RAGPromptTemplate
from app.rag.prompts.system_prompts import DEFAULT_SYSTEM_PROMPT, get_system_prompt

__all__ = ["RAGPromptTemplate", "DEFAULT_SYSTEM_PROMPT", "get_system_prompt"]

