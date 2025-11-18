# Root Level Cursor Rules

## General Principles

1. **SOLID Principles**: Follow Single Responsibility, Open/Closed, Liskov Substitution, Interface Segregation, Dependency Inversion
2. **DRY**: Don't Repeat Yourself - extract common logic into reusable functions/modules
3. **KISS**: Keep It Simple, Stupid - avoid over-engineering
4. **YAGNI**: You Aren't Gonna Need It - don't add features until needed

## Architecture Rules

1. **Clean Architecture**: Controller → Service → Repository → Database
2. **Dependency Injection**: Use FastAPI Depends() for all dependencies
3. **Async First**: All functions must be async unless explicitly synchronous
4. **No Circular Imports**: Use dependency injection to avoid circular dependencies
5. **Type Hints**: All Python functions must have type hints
6. **TypeScript**: All frontend code must use TypeScript (no .js files)

## Code Quality

1. **No Heavy Inheritance**: Prefer composition over inheritance
2. **Pure Functions**: Prefer pure functions where possible
3. **Error Handling**: Use custom exception classes with proper status codes
4. **Logging**: All operations must use structured JSON logging
5. **Testing**: Write tests for all services and critical paths (focus later per user request)

## File Organization

1. **Never Break Folder Structure**: Maintain the defined structure strictly
2. **One Class Per File**: Each class in its own file
3. **Module Organization**: Group related functionality in modules
4. **Import Organization**: Standard library → third-party → local imports

## Documentation

1. **Update Docs Before Code**: All changes must be reflected in docs first
2. **API Documentation**: All API changes must update `docs/api-design.md`
3. **RAG Documentation**: All RAG logic changes must update `docs/rag-design.md`
4. **Architecture Documentation**: System changes must update `docs/architecture.md`

## Package Management

1. **Backend**: Use `uv` for all Python package management (NOT pip)
2. **Frontend**: Use npm/pnpm/yarn as appropriate
3. **Lock Files**: Commit lock files (uv.lock, package-lock.json)

## Security

1. **Input Validation**: Validate all inputs using Pydantic schemas
2. **File Uploads**: Sanitize and validate all file uploads
3. **Environment Variables**: Never commit secrets, use .env files
4. **SQL Injection**: Use parameterized queries (SQLAlchemy handles this)

## Performance

1. **Caching**: Cache LLM responses, embeddings, and retrieval results
2. **Database Queries**: Use async queries, avoid N+1 problems
3. **Frontend**: Use React Query for caching and deduplication
4. **Background Tasks**: Use FastAPI BackgroundTasks for long-running operations

## Git

1. **Commit Messages**: Use clear, descriptive commit messages
2. **Branch Strategy**: Feature branches for new features
3. **.gitignore**: Keep .gitignore updated

## Docker

1. **Multi-stage Builds**: Use multi-stage builds for smaller images
2. **.dockerignore**: Exclude unnecessary files from Docker builds
3. **Health Checks**: Include health checks for all services

## Specific Technology Rules

### Backend (FastAPI)
- All routes must be thin - delegate to service layer
- Services must not know about FastAPI (no Request/Response objects)
- Use Pydantic for all request/response models
- Use async SQLAlchemy ORM
- Structured logging with structlog

### Frontend (React)
- Use functional components with hooks
- Use React Query for all API calls
- Atomic component design (small, reusable components)
- Avoid unnecessary re-renders (use memo, useCallback)
- TypeScript strict mode enabled

### RAG Pipeline
- Use Docling's HybridChunker (not custom chunking)
- Convert documents to Markdown as recommended by Docling
- Use Memori for memory management (from GibsonAI/Memori)
- Cache embeddings for repeated content
- Optimize token usage

## When Making Changes

1. Read the relevant `.cursor/rules.md` in the subdirectory
2. Update documentation if architecture/logic changes
3. Ensure all tests pass (when tests are added)
4. Check for linting errors
5. Verify Docker builds work

