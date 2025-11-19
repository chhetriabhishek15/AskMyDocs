"""
LLM service for Google Gemini API integration using LangChain.
"""
from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta

from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.schema import HumanMessage, SystemMessage, AIMessage, BaseMessage
from langchain.callbacks.base import BaseCallbackHandler
import structlog

from app.core.config import settings

logger = structlog.get_logger()


class LLMResponse:
    """LLM response with metadata."""

    def __init__(
        self,
        text: str,
        model: str,
        usage: Dict[str, Any] | None = None,
        finish_reason: str | None = None,
    ):
        """
        Initialize LLM response.

        Args:
            text: Response text
            model: Model used
            usage: Token usage information
            finish_reason: Reason for completion
        """
        self.text = text
        self.model = model
        self.usage = usage or {}
        self.finish_reason = finish_reason

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "text": self.text,
            "model": self.model,
            "usage": self.usage,
            "finish_reason": self.finish_reason,
        }


class LLMService:
    """Service for interacting with Google Gemini API via LangChain."""

    def __init__(
        self,
        api_key: str | None = None,
        model: str | None = None,
        temperature: float | None = None,
        max_tokens: int | None = None,
    ):
        """
        Initialize LLM service.

        Args:
            api_key: Gemini API key (defaults to settings.GEMINI_API_KEY)
            model: Model name (defaults to settings.GEMINI_MODEL)
            temperature: Temperature for generation (defaults to settings.GEMINI_TEMPERATURE)
            max_tokens: Maximum tokens (defaults to settings.GEMINI_MAX_TOKENS)
        """
        self.api_key = api_key or settings.GEMINI_API_KEY
        self.model_name = model or settings.GEMINI_MODEL
        self.temperature = temperature if temperature is not None else settings.GEMINI_TEMPERATURE
        self.max_tokens = max_tokens or settings.GEMINI_MAX_TOKENS

        # Initialize LangChain ChatGoogleGenerativeAI
        self.llm = ChatGoogleGenerativeAI(
            model=self.model_name,
            temperature=self.temperature,
            max_output_tokens=self.max_tokens,
            google_api_key=self.api_key,
        )

        # Simple in-memory cache (can be replaced with Redis later)
        self._cache: Dict[str, Dict[str, Any]] = {}
        self._cache_ttl = timedelta(seconds=settings.CACHE_LLM_RESPONSE_TTL)

        logger.info(
            "llm_service_initialized",
            model=self.model_name,
            temperature=self.temperature,
            max_tokens=self.max_tokens,
            framework="langchain",
        )

    def _get_cache_key(self, messages: List[BaseMessage], **kwargs) -> str:
        """
        Generate cache key from messages and parameters.

        Args:
            messages: List of LangChain messages
            **kwargs: Additional parameters

        Returns:
            Cache key string
        """
        import hashlib
        import json

        # Create hash from messages and relevant parameters
        messages_str = "|".join(f"{msg.__class__.__name__}:{msg.content}" for msg in messages)
        cache_data = {
            "messages": messages_str,
            "model": self.model_name,
            "temperature": self.temperature,
            **kwargs,
        }
        cache_str = json.dumps(cache_data, sort_keys=True)
        return hashlib.md5(cache_str.encode()).hexdigest()

    def _get_from_cache(self, cache_key: str) -> Optional[LLMResponse]:
        """
        Get response from cache if available and not expired.

        Args:
            cache_key: Cache key

        Returns:
            Cached response or None
        """
        if cache_key not in self._cache:
            return None

        cached = self._cache[cache_key]
        cached_time = cached.get("timestamp")
        
        if cached_time:
            age = datetime.utcnow() - cached_time
            if age > self._cache_ttl:
                # Cache expired
                del self._cache[cache_key]
                return None

        logger.debug("llm_cache_hit", cache_key=cache_key[:8])
        return cached.get("response")

    def _store_in_cache(self, cache_key: str, response: LLMResponse) -> None:
        """
        Store response in cache.

        Args:
            cache_key: Cache key
            response: LLM response
        """
        self._cache[cache_key] = {
            "response": response,
            "timestamp": datetime.utcnow(),
        }
        logger.debug("llm_cache_store", cache_key=cache_key[:8])

    async def generate(
        self,
        prompt: str,
        system_prompt: str | None = None,
        use_cache: bool = True,
        callbacks: List[BaseCallbackHandler] | None = None,
        **kwargs,
    ) -> LLMResponse:
        """
        Generate response from LLM.

        Args:
            prompt: User prompt
            system_prompt: Optional system prompt
            use_cache: Whether to use cache
            callbacks: Optional LangChain callbacks (for Memori integration)
            **kwargs: Additional generation parameters

        Returns:
            LLMResponse object

        Raises:
            ValueError: If generation fails
        """
        try:
            # Build messages list
            messages: List[BaseMessage] = []
            
            if system_prompt:
                messages.append(SystemMessage(content=system_prompt))
            
            messages.append(HumanMessage(content=prompt))

            # Check cache
            if use_cache:
                cache_key = self._get_cache_key(messages, **kwargs)
                cached_response = self._get_from_cache(cache_key)
                if cached_response:
                    return cached_response

            logger.info(
                "llm_generation_started",
                model=self.model_name,
                prompt_length=len(prompt),
            )

            # Generate response using LangChain
            response = await self.llm.ainvoke(
                messages,
                config={"callbacks": callbacks} if callbacks else None,
            )

            # Extract response text
            response_text = response.content if hasattr(response, "content") else str(response)

            # Extract usage information if available
            usage = {}
            if hasattr(response, "response_metadata"):
                metadata = response.response_metadata
                usage = {
                    "prompt_tokens": metadata.get("prompt_token_count", 0),
                    "completion_tokens": metadata.get("completion_token_count", 0),
                    "total_tokens": metadata.get("total_token_count", 0),
                }

            # Extract finish reason if available
            finish_reason = None
            if hasattr(response, "response_metadata"):
                finish_reason = response.response_metadata.get("finish_reason")

            llm_response = LLMResponse(
                text=response_text,
                model=self.model_name,
                usage=usage,
                finish_reason=finish_reason,
            )

            # Cache response
            if use_cache:
                cache_key = self._get_cache_key(messages, **kwargs)
                self._store_in_cache(cache_key, llm_response)

            logger.info(
                "llm_generation_completed",
                model=self.model_name,
                response_length=len(response_text),
            )

            return llm_response

        except Exception as e:
            logger.error("llm_generation_error", model=self.model_name, error=str(e))
            raise ValueError(f"Failed to generate response: {e}") from e

    async def generate_from_messages(
        self,
        messages: List[BaseMessage],
        use_cache: bool = True,
        callbacks: List[BaseCallbackHandler] | None = None,
        **kwargs,
    ) -> LLMResponse:
        """
        Generate response from LangChain messages.

        Args:
            messages: List of LangChain BaseMessage objects
            use_cache: Whether to use cache
            callbacks: Optional LangChain callbacks
            **kwargs: Additional parameters

        Returns:
            LLMResponse object
        """
        try:
            # Check cache
            if use_cache:
                cache_key = self._get_cache_key(messages, **kwargs)
                cached_response = self._get_from_cache(cache_key)
                if cached_response:
                    return cached_response

            logger.info(
                "llm_generation_started",
                model=self.model_name,
                num_messages=len(messages),
            )

            # Generate response
            response = await self.llm.ainvoke(
                messages,
                config={"callbacks": callbacks} if callbacks else None,
            )

            # Extract response text
            response_text = response.content if hasattr(response, "content") else str(response)

            # Extract usage information
            usage = {}
            if hasattr(response, "response_metadata"):
                metadata = response.response_metadata
                usage = {
                    "prompt_tokens": metadata.get("prompt_token_count", 0),
                    "completion_tokens": metadata.get("completion_token_count", 0),
                    "total_tokens": metadata.get("total_token_count", 0),
                }

            finish_reason = None
            if hasattr(response, "response_metadata"):
                finish_reason = response.response_metadata.get("finish_reason")

            llm_response = LLMResponse(
                text=response_text,
                model=self.model_name,
                usage=usage,
                finish_reason=finish_reason,
            )

            # Cache response
            if use_cache:
                cache_key = self._get_cache_key(messages, **kwargs)
                self._store_in_cache(cache_key, llm_response)

            logger.info(
                "llm_generation_completed",
                model=self.model_name,
                response_length=len(response_text),
            )

            return llm_response

        except Exception as e:
            logger.error("llm_generation_error", model=self.model_name, error=str(e))
            raise ValueError(f"Failed to generate response: {e}") from e

    def clear_cache(self) -> int:
        """
        Clear the response cache.

        Returns:
            Number of entries cleared
        """
        count = len(self._cache)
        self._cache.clear()
        logger.info("llm_cache_cleared", entries_cleared=count)
        return count
