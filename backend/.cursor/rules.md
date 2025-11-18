# Backend Cursor Rules

## FastAPI Patterns

1. **Async First**: All route handlers must be async
2. **Dependency Injection**: Use FastAPI Depends() for all dependencies
3. **Thin Controllers**: Routes delegate to service layer immediately
4. **Pydantic Schemas**: Use Pydantic for all request/response validation
5. **Status Codes**: Use appropriate HTTP status codes

## Architecture Layers

1. **Controller (API Routes)**: Handle HTTP requests/responses only
2. **Service Layer**: Business logic, orchestration
3. **Repository Layer**: Data access, database operations
4. **Models**: SQLAlchemy ORM models
5. **Schemas**: Pydantic models for validation

## Service Layer Rules

1. **No FastAPI Dependencies**: Services must not import FastAPI (Request, Response, etc.)
2. **Pure Business Logic**: Services contain business logic only
3. **Async Functions**: All service methods must be async
4. **Error Handling**: Raise custom exceptions, let middleware handle HTTP responses
5. **Dependency Injection**: Services receive dependencies via constructor

## Repository Layer Rules

1. **Database Only**: Repositories only interact with database
2. **SQLAlchemy Async**: Use async SQLAlchemy (asyncpg driver)
3. **No Business Logic**: Repositories only do CRUD operations
4. **Transaction Management**: Use async context managers for sessions

## Database

1. **Async SQLAlchemy**: Use `AsyncSession` from SQLAlchemy
2. **Connection Pooling**: Configure connection pool appropriately
3. **Migrations**: Use Alembic for database migrations
4. **pgvector**: Use pgvector extension for vector operations
5. **Indexes**: Create indexes for frequently queried columns

## Error Handling

1. **Custom Exceptions**: Create custom exception classes
2. **Exception Handlers**: Register exception handlers in FastAPI app
3. **Structured Errors**: Return consistent error response format
4. **Logging**: Log all exceptions with context

## Logging

1. **Structured Logging**: Use structlog for JSON structured logs
2. **Log Levels**: Use appropriate log levels (DEBUG, INFO, WARNING, ERROR)
3. **Request Logging**: Log all requests/responses in middleware
4. **Context**: Include request ID, user ID, etc. in logs

## Caching

1. **LLM Responses**: Cache LLM responses with TTL
2. **Embeddings**: Cache embeddings for repeated content
3. **Vector Search**: Cache retrieval results
4. **In-Memory First**: Start with in-memory cache, move to Redis later

## Background Tasks

1. **FastAPI BackgroundTasks**: Use for simple background tasks
2. **Task Queue**: Plan for Celery/Redis in future
3. **Task Status**: Track task status in database
4. **Error Handling**: Handle and log background task errors

## File Organization

```
app/
├── api/              # FastAPI routes/controllers
│   ├── routes/       # Route modules
│   └── dependencies.py
├── services/         # Business logic layer
├── repositories/     # Data access layer
├── models/           # SQLAlchemy ORM models
├── schemas/          # Pydantic models
├── rag/              # RAG pipeline components
├── vectorstore/      # pgvector operations
├── core/             # Config, DI, exceptions
├── utils/            # Utility functions
└── logging/          # Logging configuration
```

## Type Hints

1. **All Functions**: Every function must have type hints
2. **Return Types**: Always specify return types
3. **Optional/Union**: Use Optional, Union types appropriately
4. **Generic Types**: Use generics for reusable functions

## Package Management

1. **uv Only**: Use `uv` for all package management (NOT pip)
2. **pyproject.toml**: Use pyproject.toml for project configuration
3. **Dependencies**: Pin versions in pyproject.toml
4. **Lock File**: Commit uv.lock file

## Testing (Future)

1. **PyTest**: Use pytest for all tests
2. **Async Tests**: Use pytest-asyncio for async tests
3. **Fixtures**: Use pytest fixtures for test data
4. **Mocking**: Mock external services (Gemini API, etc.)
5. **Coverage**: Aim for 80%+ test coverage

## Code Quality

1. **Black**: Use Black for code formatting (or similar)
2. **Ruff**: Use Ruff for linting
3. **Import Order**: Standard library → third-party → local imports
4. **Docstrings**: Use docstrings for all public functions/classes

## Common Patterns

### Route Pattern
```python
@router.post("/resource")
async def create_resource(
    data: ResourceCreate,
    service: ResourceService = Depends(get_resource_service)
):
    result = await service.create(data)
    return result
```

### Service Pattern
```python
class ResourceService:
    def __init__(self, repo: ResourceRepository):
        self.repo = repo
    
    async def create(self, data: ResourceCreate) -> Resource:
        # Business logic
        resource = await self.repo.create(data)
        return resource
```

### Repository Pattern
```python
class ResourceRepository:
    def __init__(self, session: AsyncSession):
        self.session = session
    
    async def create(self, data: ResourceCreate) -> ResourceModel:
        resource = ResourceModel(**data.dict())
        self.session.add(resource)
        await self.session.commit()
        return resource
```

## Docling Integration

1. **Use HybridChunker**: Use Docling's HybridChunker, not custom chunking
2. **Markdown Conversion**: Convert documents to Markdown as recommended
3. **Configuration**: Use environment variables for chunking parameters
4. **Error Handling**: Handle Docling parsing errors gracefully

## Memori Integration

1. **Memory Service**: Create service wrapper around Memori
2. **Session Management**: Use session_id for memory isolation
3. **Context Retrieval**: Retrieve relevant memories before LLM call
4. **Memory Storage**: Store interactions after LLM response

## Security

1. **Input Validation**: Validate all inputs with Pydantic
2. **File Uploads**: Validate file types, sizes, sanitize filenames
3. **SQL Injection**: SQLAlchemy handles this, but be aware
4. **CORS**: Configure CORS appropriately
5. **Rate Limiting**: Implement rate limiting middleware

