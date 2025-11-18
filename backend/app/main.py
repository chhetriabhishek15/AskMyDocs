"""
FastAPI application entry point.
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.core.config import settings
from app.core.logging import setup_logging
from app.api.routes import health, upload, chat, documents, conversations
from app.middleware.logging_middleware import LoggingMiddleware
from app.middleware.exception_handler import setup_exception_handlers

# Setup structured logging
setup_logging()

# Create FastAPI app
app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    description="Tiramai RAG System API",
    docs_url="/docs",
    redoc_url="/redoc",
)

# Setup CORS
# CORS_ORIGINS is converted to list by model_validator, but handle both cases for safety
cors_origins: list = (
    settings.CORS_ORIGINS 
    if isinstance(settings.CORS_ORIGINS, list) 
    else settings.cors_origins_list
)
app.add_middleware(
    CORSMiddleware,
    allow_origins=cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Add logging middleware
app.add_middleware(LoggingMiddleware)

# Setup exception handlers
setup_exception_handlers(app)

# Include routers
app.include_router(health.router, prefix="/api/v1", tags=["health"])
app.include_router(upload.router, prefix="/api/v1", tags=["upload"])
app.include_router(chat.router, prefix="/api/v1", tags=["chat"])
app.include_router(documents.router, prefix="/api/v1", tags=["documents"])
app.include_router(conversations.router, prefix="/api/v1", tags=["conversations"])


@app.on_event("startup")
async def startup_event():
    """Initialize services on startup."""
    import structlog

    logger = structlog.get_logger()
    logger.info("application_started", version=settings.APP_VERSION)


@app.on_event("shutdown")
async def shutdown_event():
    """Cleanup on shutdown."""
    import structlog

    logger = structlog.get_logger()
    logger.info("application_shutdown")


