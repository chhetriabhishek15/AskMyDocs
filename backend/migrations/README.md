# Database Migrations

This directory contains database initialization and migration scripts.

## Initialization

The `init.sql` file is automatically executed when the PostgreSQL container starts for the first time. It:

1. Enables the pgvector extension
2. Creates the required tables (documents, chunks, conversations)
3. Creates indexes for performance

## Schema

- **documents**: Stores uploaded document metadata and markdown content
- **chunks**: Stores document chunks with vector embeddings (384 dimensions)
- **conversations**: Stores chat conversation history

## Future Migrations

For future schema changes, use Alembic migrations:

```bash
# Generate migration
alembic revision --autogenerate -m "description"

# Apply migration
alembic upgrade head
```


