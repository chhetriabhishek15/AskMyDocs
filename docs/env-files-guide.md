# Environment Files Guide

This project uses **two separate `.env` files** for different purposes:

## File Structure

```
tiramai-rag/
├── .env                    # For Docker Compose (database credentials, ports)
└── backend/
    └── .env                # For FastAPI application (API keys, app config)
```

## 1. Root `.env` (Docker Compose)

**Location:** `/.env` (project root)

**Purpose:** Configuration for Docker Compose services

**Used by:**
- `docker-compose.yml` - PostgreSQL container, service ports
- Docker Compose environment variable substitution

**Content:**
```env
# PostgreSQL Configuration (for Docker container)
POSTGRES_USER=tiramai_user
POSTGRES_PASSWORD=tiramai_password
POSTGRES_DB=tiramai_db
POSTGRES_PORT=5432

# Service Ports
BACKEND_PORT=8000
FRONTEND_PORT=3000

# Frontend API URL
VITE_API_URL=http://localhost:8000/api/v1
```

**When to use:**
- Setting database credentials for PostgreSQL container
- Changing service ports
- Docker-specific configuration

---

## 2. Backend `.env` (FastAPI Application)

**Location:** `/backend/.env`

**Purpose:** Configuration for the FastAPI backend application

**Used by:**
- `backend/app/core/config.py` - Pydantic Settings
- FastAPI application at runtime

**Content:**
```env
# Database Connection (for application)
# Note: Use 'postgres' as hostname when running in Docker
DATABASE_URL=postgresql+asyncpg://tiramai_user:tiramai_password@postgres:5432/tiramai_db

# Embedding Model
EMBEDDING_MODEL=sentence-transformers/all-MiniLM-L6-v2
EMBEDDING_DIMENSION=384

# Docling Chunking
CHUNK_SIZE=512
CHUNK_OVERLAP=50
MIN_CHUNK_SIZE=100

# Retrieval
TOP_K_RETRIEVAL=5
MIN_SIMILARITY_SCORE=0.7

# LLM Configuration
GEMINI_API_KEY=your_actual_gemini_api_key_here
GEMINI_MODEL=gemini-pro
GEMINI_TEMPERATURE=0.7
GEMINI_MAX_TOKENS=2048

# Memori Configuration
MEMORI_DATABASE_CONNECTION=postgresql://tiramai_user:tiramai_password@postgres:5432/tiramai_db
MEMORI_CONSCIOUS_INGEST=true
MEMORI_AUTO_INGEST=true
MEMORI_NAMESPACE=production

# Application
APP_NAME=Tiramai RAG
APP_VERSION=1.0.0
DEBUG=true
LOG_LEVEL=INFO

# CORS (comma-separated, no quotes)
CORS_ORIGINS=http://localhost:3000,http://localhost:5173

# File Upload
MAX_FILE_SIZE=104857600
ALLOWED_FILE_TYPES=pdf,docx,doc,zip,txt,md

# Rate Limiting
RATE_LIMIT_CHAT=10/minute
RATE_LIMIT_UPLOAD=5/minute
RATE_LIMIT_DEFAULT=100/minute

# Cache TTL (seconds)
CACHE_EMBEDDING_TTL=86400
CACHE_LLM_RESPONSE_TTL=3600
CACHE_RETRIEVAL_TTL=1800

# Background Tasks
TASK_TIMEOUT=3600
```

**When to use:**
- API keys (Gemini, etc.)
- Application-specific settings
- Feature flags
- Business logic configuration

---

## Important Notes

### Database Connection

**When running in Docker:**
```env
# backend/.env
DATABASE_URL=postgresql+asyncpg://tiramai_user:tiramai_password@postgres:5432/tiramai_db
#                                                                    ^^^^^^^^
#                                                                    Use 'postgres' (service name)
```

**When running locally (outside Docker):**
```env
# backend/.env
DATABASE_URL=postgresql+asyncpg://tiramai_user:tiramai_password@localhost:5432/tiramai_db
#                                                                    ^^^^^^^^^^
#                                                                    Use 'localhost'
```

### Variable Precedence

When running in Docker:
1. `docker-compose.yml` environment section (highest priority)
2. `backend/.env` file
3. Root `.env` file (for Docker Compose variables)
4. Default values in code

### Keeping Values in Sync

**Database credentials** should match between:
- Root `.env`: `POSTGRES_USER`, `POSTGRES_PASSWORD`, `POSTGRES_DB`
- `backend/.env`: `DATABASE_URL` and `MEMORI_DATABASE_CONNECTION`

**Example sync:**
```bash
# Root .env
POSTGRES_USER=myuser
POSTGRES_PASSWORD=mypass
POSTGRES_DB=mydb

# backend/.env (must match)
DATABASE_URL=postgresql+asyncpg://myuser:mypass@postgres:5432/mydb
MEMORI_DATABASE_CONNECTION=postgresql://myuser:mypass@postgres:5432/mydb
```

---

## Setup Instructions

### 1. Create Root `.env`

```bash
# In project root
cat > .env << EOF
POSTGRES_USER=tiramai_user
POSTGRES_PASSWORD=tiramai_password
POSTGRES_DB=tiramai_db
POSTGRES_PORT=5432
BACKEND_PORT=8000
FRONTEND_PORT=3000
VITE_API_URL=http://localhost:8000/api/v1
EOF
```

### 2. Create Backend `.env`

```bash
# In backend directory
cd backend
# Copy from template or create manually
# See backend/ENV_TEMPLATE.txt or docs/setup-guide.md
```

### 3. Verify Both Files

```bash
# Check root .env
cat .env

# Check backend .env
cat backend/.env
```

---

## Git Ignore

Both files are already in `.gitignore`:
- `.env` (root)
- `backend/.env`

**Never commit these files!**

---

## Troubleshooting

### Issue: Database connection fails in Docker

**Check:**
1. Root `.env` has correct `POSTGRES_USER`, `POSTGRES_PASSWORD`, `POSTGRES_DB`
2. `backend/.env` has `DATABASE_URL` with:
   - Correct credentials (matching root `.env`)
   - Hostname `postgres` (not `localhost`) when in Docker
   - Correct database name

### Issue: Backend can't find environment variables

**Check:**
1. `backend/.env` exists
2. Variables are spelled correctly (case-sensitive)
3. No quotes around values (except for strings that need quotes)
4. Running from `backend/` directory or using absolute path

### Issue: Docker Compose can't find variables

**Check:**
1. Root `.env` exists in project root
2. Variables use correct names (matching docker-compose.yml)
3. No spaces around `=` sign: `VAR=value` not `VAR = value`

---

## Best Practices

1. **Use different passwords for dev/prod**
   - Development: Use defaults or simple passwords
   - Production: Use strong, randomly generated passwords

2. **Keep credentials in sync**
   - When changing root `.env` database credentials, update `backend/.env` too

3. **Use environment-specific files**
   - `.env.development`
   - `.env.production`
   - Load with: `docker-compose --env-file .env.production up -d`

4. **Document required variables**
   - Keep `.env.example` files (without real secrets)
   - Document in README or setup guide

