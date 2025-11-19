"""
Application configuration using Pydantic Settings.
"""
from typing import List, Union, Any, Dict
from pydantic import field_validator, model_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings."""

    # Application
    APP_NAME: str = "Tiramai RAG"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = False
    LOG_LEVEL: str = "INFO"

    # ChromaDB Configuration
    CHROMA_DB_PATH: str = "./chroma_db"  # Persistent storage path
    CHROMA_COLLECTION_NAME: str = "documents"
    # ChromaDB handles embeddings internally - can use default or custom embedding function
    CHROMA_EMBEDDING_FUNCTION: str | None = None  # None = use default, or specify custom function

    # Docling Chunking
    CHUNK_SIZE: int = 512  # Max tokens per chunk
    CHUNK_OVERLAP: int = 50  # Not used by HybridChunker (uses merge_peers instead)
    MIN_CHUNK_SIZE: int = 100  # Not used by HybridChunker
    CHUNKER_TOKENIZER_MODEL: str = "sentence-transformers/all-MiniLM-L6-v2"  # Tokenizer for HybridChunker
    CHUNKER_MERGE_PEERS: bool = True  # Merge small adjacent chunks

    # Retrieval
    TOP_K_RETRIEVAL: int = 5
    MIN_SIMILARITY_SCORE: float = 0.5  # Lowered from 0.7 - actual scores are typically 0.55-0.65

    # LLM
    GEMINI_API_KEY: str
    GEMINI_MODEL: str = "gemini-pro"
    GEMINI_TEMPERATURE: float = 0.7
    GEMINI_MAX_TOKENS: int = 2048

    # Memori Configuration
    MEMORI_DATABASE_CONNECTION: str | None = None  # PostgreSQL/SQLite connection string
    MEMORI_USE_SQLITE_FALLBACK: bool = True  # Use SQLite if ChromaDB format not supported
    MEMORI_SQLITE_PATH: str = "./memory.db"  # Path for SQLite fallback
    MEMORI_CONSCIOUS_INGEST: bool = True  # Short-term working memory
    MEMORI_AUTO_INGEST: bool = True  # Dynamic search per query
    MEMORI_NAMESPACE: str = "production"  # Memory namespace for isolation

    # CORS - Store as string in .env, converted to list by validator
    CORS_ORIGINS: Union[str, List[str]] = "http://localhost:3000,http://localhost:5173"

    # File Upload
    MAX_FILE_SIZE: int = 104857600  # 100MB
    # Store as string in .env, converted to list by validator
    ALLOWED_FILE_TYPES: Union[str, List[str]] = "pdf,docx,doc,zip,txt,md"

    @model_validator(mode="after")
    def parse_list_fields(self) -> "Settings":
        """Parse comma-separated strings into lists after model creation."""
        # Parse CORS_ORIGINS
        if isinstance(self.CORS_ORIGINS, str):
            cors_list = [origin.strip() for origin in self.CORS_ORIGINS.split(",") if origin.strip()]
            object.__setattr__(self, "CORS_ORIGINS", cors_list)
        
        # Parse ALLOWED_FILE_TYPES
        if isinstance(self.ALLOWED_FILE_TYPES, str):
            file_types_list = [ft.strip() for ft in self.ALLOWED_FILE_TYPES.split(",") if ft.strip()]
            object.__setattr__(self, "ALLOWED_FILE_TYPES", file_types_list)
        
        return self

    @property
    def cors_origins_list(self) -> List[str]:
        """Get CORS origins as a list."""
        if isinstance(self.CORS_ORIGINS, list):
            return self.CORS_ORIGINS
        return [origin.strip() for origin in self.CORS_ORIGINS.split(",") if origin.strip()]

    @property
    def allowed_file_types_list(self) -> List[str]:
        """Get allowed file types as a list."""
        if isinstance(self.ALLOWED_FILE_TYPES, list):
            return self.ALLOWED_FILE_TYPES
        return [ft.strip() for ft in self.ALLOWED_FILE_TYPES.split(",") if ft.strip()]

    # Rate Limiting
    RATE_LIMIT_CHAT: str = "10/minute"
    RATE_LIMIT_UPLOAD: str = "5/minute"
    RATE_LIMIT_DEFAULT: str = "100/minute"

    # Cache TTL (seconds)
    CACHE_EMBEDDING_TTL: int = 86400  # 24 hours
    CACHE_LLM_RESPONSE_TTL: int = 3600  # 1 hour
    CACHE_RETRIEVAL_TTL: int = 1800  # 30 minutes

    # Background Tasks
    TASK_TIMEOUT: int = 3600  # 1 hour

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=True,
        extra="ignore",
    )


settings = Settings()


