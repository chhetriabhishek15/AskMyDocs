# Docker Compose Setup Guide

This guide provides detailed instructions for running the entire Tiramai RAG system using Docker Compose.

## Overview

Docker Compose orchestrates three services:
1. **PostgreSQL** - Database with pgvector extension
2. **Backend** - FastAPI application
3. **Frontend** - React application

## Prerequisites

- Docker Desktop installed and running
- Docker Compose (included with Docker Desktop)
- At least 4GB RAM available for Docker

## Step-by-Step Setup

### Step 1: Verify Docker is Running

```bash
# Check Docker is running
docker --version
docker-compose --version

# Verify Docker Desktop is running (should show containers/images)
docker ps
```

### Step 2: Create Environment Files

#### Root `.env` File

Create `.env` in the project root (`F:\Tiramai\.env`):

```env
# PostgreSQL Configuration
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

#### Backend `.env` File

Create `backend/.env`:

```env
# Database (use 'postgres' hostname - Docker service name)
DATABASE_URL=postgresql+asyncpg://tiramai_user:tiramai_password@postgres:5432/tiramai_db

# LLM Configuration
GEMINI_API_KEY=your_gemini_api_key_here
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

# CORS (comma-separated)
CORS_ORIGINS=http://localhost:3000,http://localhost:5173

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

**Important Notes:**
- Replace `your_gemini_api_key_here` with your actual Gemini API key
- Use `postgres` as the hostname in `DATABASE_URL` (Docker service name)
- Use `localhost` only when running backend locally (outside Docker)

### Step 3: Build and Start Services

```bash
# From project root (F:\Tiramai)

# Build images and start all services
docker-compose up -d

# Or build without cache (if you have issues)
docker-compose build --no-cache
docker-compose up -d
```

**What happens:**
1. PostgreSQL container starts first
2. Database initialization script runs (`backend/migrations/init.sql`)
3. Backend waits for PostgreSQL to be healthy
4. Backend container starts
5. Frontend container starts

### Step 4: Verify Services

```bash
# Check service status
docker-compose ps

# Expected output:
# NAME                STATUS          PORTS
# tiramai-backend     Up (healthy)    0.0.0.0:8000->8000/tcp
# tiramai-frontend    Up (healthy)    0.0.0.0:3000->3000/tcp
# tiramai-postgres    Up (healthy)    0.0.0.0:5432->5432/tcp
```

### Step 5: Check Logs

```bash
# View all logs
docker-compose logs -f

# View specific service logs
docker-compose logs -f backend
docker-compose logs -f frontend
docker-compose logs -f postgres

# View last 100 lines
docker-compose logs --tail=100 backend
```

### Step 6: Test the Application

#### Backend Health Check
```bash
curl http://localhost:8000/api/v1/health

# Or visit in browser
http://localhost:8000/api/v1/health
```

**Expected Response:**
```json
{
  "status": "healthy",
  "timestamp": "2024-01-01T00:00:00Z"
}
```

#### Frontend
Open browser: http://localhost:3000

#### API Documentation
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

## Common Commands

### Start/Stop Services

```bash
# Start all services
docker-compose up -d

# Stop all services (keeps data)
docker-compose down

# Stop and remove volumes (deletes database data)
docker-compose down -v

# Restart a specific service
docker-compose restart backend

# Start only PostgreSQL
docker-compose up -d postgres

# Start backend and frontend (if postgres already running)
docker-compose up -d backend frontend
```

### View Logs

```bash
# Follow logs (real-time)
docker-compose logs -f

# View logs for specific service
docker-compose logs -f backend

# View last N lines
docker-compose logs --tail=50 backend
```

### Rebuild Services

```bash
# Rebuild specific service
docker-compose build backend

# Rebuild all services
docker-compose build

# Rebuild without cache
docker-compose build --no-cache
```

### Database Access

```bash
# Connect to PostgreSQL from host
docker exec -it tiramai-postgres psql -U tiramai_user -d tiramai_db

# Run SQL command
docker exec tiramai-postgres psql -U tiramai_user -d tiramai_db -c "SELECT version();"

# Check pgvector extension
docker exec tiramai-postgres psql -U tiramai_user -d tiramai_db -c "SELECT * FROM pg_extension WHERE extname = 'vector';"
```

### Container Shell Access

```bash
# Access backend container
docker exec -it tiramai-backend bash

# Access frontend container
docker exec -it tiramai-frontend sh

# Access postgres container
docker exec -it tiramai-postgres bash
```

## Troubleshooting

### Services Won't Start

**Check Docker Desktop:**
```bash
# Verify Docker is running
docker ps

# Check Docker resources (Settings > Resources in Docker Desktop)
# Ensure at least 4GB RAM allocated
```

**Check Logs:**
```bash
docker-compose logs
```

**Rebuild:**
```bash
docker-compose down
docker-compose build --no-cache
docker-compose up -d
```

### Port Already in Use

**Change ports in root `.env`:**
```env
BACKEND_PORT=8001
FRONTEND_PORT=3001
POSTGRES_PORT=5433
```

Then restart:
```bash
docker-compose down
docker-compose up -d
```

### Database Connection Errors

**Verify credentials match:**
- Root `.env`: `POSTGRES_USER`, `POSTGRES_PASSWORD`, `POSTGRES_DB`
- `backend/.env`: `DATABASE_URL` and `MEMORI_DATABASE_CONNECTION`

**Check PostgreSQL is healthy:**
```bash
docker-compose ps postgres
docker-compose logs postgres
```

**Reset database (WARNING: deletes all data):**
```bash
docker-compose down -v
docker-compose up -d postgres
# Wait for it to be healthy, then start other services
docker-compose up -d
```

### Backend Won't Start

**Check logs:**
```bash
docker-compose logs backend
```

**Common issues:**
- Missing `GEMINI_API_KEY` in `backend/.env`
- Database not ready (wait for postgres health check)
- Port conflict (change `BACKEND_PORT` in root `.env`)

**Rebuild backend:**
```bash
docker-compose build --no-cache backend
docker-compose up -d backend
```

### Frontend Can't Connect to Backend

**Check:**
1. Backend is running: `curl http://localhost:8000/api/v1/health`
2. `VITE_API_URL` in root `.env` matches backend port
3. CORS settings in `backend/.env` include frontend URL

**View frontend logs:**
```bash
docker-compose logs frontend
```

### Volume Issues

**List volumes:**
```bash
docker volume ls
```

**Inspect volume:**
```bash
docker volume inspect tiramai_postgres_data
```

**Remove volumes (WARNING: deletes data):**
```bash
docker-compose down -v
docker volume prune  # Remove unused volumes
```

## Development Workflow

### Hot Reload

Both backend and frontend support hot reload:
- **Backend**: Code changes in `backend/` automatically reload (via volume mount)
- **Frontend**: Code changes in `frontend/` automatically reload (via volume mount)

### Making Changes

1. Edit code in `backend/` or `frontend/`
2. Changes are automatically reflected (no rebuild needed)
3. Check logs: `docker-compose logs -f backend`

### Adding Dependencies

**Backend:**
```bash
# Edit backend/pyproject.toml
# Then rebuild
docker-compose build backend
docker-compose up -d backend
```

**Frontend:**
```bash
# Edit frontend/package.json
# Then rebuild
docker-compose build frontend
docker-compose up -d frontend
```

## Production Considerations

For production deployment:

1. **Remove volume mounts** (code should be in image, not mounted)
2. **Use production builds** (frontend should use `npm run build`)
3. **Set `DEBUG=false`** in `backend/.env`
4. **Use secrets management** (don't commit `.env` files)
5. **Configure reverse proxy** (nginx/traefik)
6. **Set up SSL/TLS**
7. **Configure backups** for PostgreSQL volumes

## Next Steps

After Docker Compose setup is working:
1. ✅ All services running
2. ✅ Health checks passing
3. ✅ Frontend accessible
4. ✅ Backend API accessible

Proceed to **Phase 2: RAG Ingestion Pipeline**!
