# Tiramai RAG System - Setup Guide

This guide provides step-by-step instructions for setting up the development environment.

## Prerequisites

- Python 3.11+ installed
- Node.js 20+ and npm/pnpm/yarn installed
- Docker and Docker Compose installed
- uv package manager installed ([Installation Guide](https://docs.astral.sh/uv/getting-started/installation/))

## Step-by-Step Setup

### Step 1: Clone/Verify Project Structure

Ensure you're in the project root directory:
```bash
cd F:\Tiramai
```

Project structure should be:
```
tiramai-rag/
├── backend/
├── frontend/
├── docs/
├── docker-compose.yml
└── .env.example
```

---

### Step 2: Backend Setup with uv

#### 2.1 Navigate to Backend Directory
```bash
cd backend
```

#### 2.2 Create Virtual Environment with uv
```bash
uv venv
```

This creates `.venv` in the `backend/` directory:
```
backend/
├── .venv/          ← Virtual environment here
├── app/
├── pyproject.toml
└── uv.lock
```

#### 2.3 Install Dependencies
```bash
uv sync
```

This will:
- Create/update `uv.lock` file
- Install all dependencies from `pyproject.toml`
- Install the project in editable mode

#### 2.4 Activate Virtual Environment

**Windows (PowerShell):**
```powershell
.\.venv\Scripts\Activate.ps1
```

**Windows (CMD):**
```cmd
.venv\Scripts\activate.bat
```

**Linux/Mac:**
```bash
source .venv/bin/activate
```

After activation, you should see `(.venv)` in your terminal prompt.

#### 2.5 Verify Backend Installation
```bash
# Check Python version
python --version  # Should be 3.11+

# Check if FastAPI is installed
python -c "import fastapi; print(fastapi.__version__)"
```

---

### Step 3: Frontend Setup

#### 3.1 Navigate to Frontend Directory
```bash
cd ..\frontend
# or from root: cd frontend
```

#### 3.2 Install Dependencies
```bash
npm install
```

This creates `node_modules/` in the `frontend/` directory:
```
frontend/
├── node_modules/   ← Dependencies here
├── src/
├── package.json
└── package-lock.json
```

#### 3.3 Verify Frontend Installation
```bash
# Check Node version
node --version  # Should be 20+

# Check npm version
npm --version
```

---

### Step 4: Environment Variables Setup

#### 4.1 Create .env File in Backend

**Location:** `backend/.env`

```bash
cd backend
# Create .env file (copy from .env.example if it exists)
```

**Content for `backend/.env`:**
```env
# Database
DATABASE_URL=postgresql+asyncpg://tiramai_user:tiramai_password@localhost:5432/tiramai_db

# Embedding Model
EMBEDDING_MODEL=sentence-transformers/all-MiniLM-L6-v2
EMBEDDING_DIMENSION=384

# Docling Chunking Configuration
CHUNK_SIZE=512
CHUNK_OVERLAP=50
MIN_CHUNK_SIZE=100

# Retrieval Configuration
TOP_K_RETRIEVAL=5
MIN_SIMILARITY_SCORE=0.7

# LLM Configuration
GEMINI_API_KEY=your_gemini_api_key_here
GEMINI_MODEL=gemini-pro
GEMINI_TEMPERATURE=0.7
GEMINI_MAX_TOKENS=2048

# Memori Configuration
MEMORI_DATABASE_CONNECTION=postgresql://tiramai_user:tiramai_password@localhost:5432/tiramai_db
MEMORI_CONSCIOUS_INGEST=true
MEMORI_AUTO_INGEST=true
MEMORI_NAMESPACE=production

# Application
APP_NAME=Tiramai RAG
APP_VERSION=1.0.0
DEBUG=true
LOG_LEVEL=INFO

# CORS
CORS_ORIGINS=http://localhost:3000,http://localhost:5173

# File Upload
MAX_FILE_SIZE=104857600
ALLOWED_FILE_TYPES=pdf,docx,doc,zip,txt,md

# Rate Limiting
RATE_LIMIT_CHAT=10/minute
RATE_LIMIT_UPLOAD=5/minute
RATE_LIMIT_DEFAULT=100/minute

# Cache TTL (in seconds)
CACHE_EMBEDDING_TTL=86400
CACHE_LLM_RESPONSE_TTL=3600
CACHE_RETRIEVAL_TTL=1800

# Background Tasks
TASK_TIMEOUT=3600
```

#### 4.2 Create .env File in Frontend (Optional)

**Location:** `frontend/.env`

```bash
cd frontend
```

**Content for `frontend/.env`:**
```env
VITE_API_URL=http://localhost:8000/api/v1
```

**Note:** Frontend can also use `vite.config.ts` proxy, so this is optional.

---

### Step 5: Start PostgreSQL with Docker Compose

#### 5.1 Navigate to Project Root
```bash
cd F:\Tiramai
```

#### 5.2 Start Only PostgreSQL Service
```bash
docker-compose up -d postgres
```

This starts only the PostgreSQL container with pgvector.

#### 5.3 Verify PostgreSQL is Running
```bash
docker-compose ps
```

You should see `tiramai-postgres` running.

#### 5.4 Check Database Connection (Optional)
```bash
# Using psql (if installed)
psql -h localhost -U tiramai_user -d tiramai_db

# Or using Docker
docker exec -it tiramai-postgres psql -U tiramai_user -d tiramai_db
```

---

### Step 6: Run Backend (Development Mode)

#### 6.1 Navigate to Backend
```bash
cd backend
```

#### 6.2 Activate Virtual Environment (if not already)
```powershell
.\.venv\Scripts\Activate.ps1
```

#### 6.3 Run FastAPI with uvicorn
```bash
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

**Expected Output:**
```
INFO:     Will watch for changes in these directories: ['F:\\Tiramai\\backend']
INFO:     Uvicorn running on http://0.0.0.0:8000 (Press CTRL+C to quit)
INFO:     Started reloader process [xxxxx] using WatchFiles
INFO:     Started server process [xxxxx]
INFO:     Waiting for application startup.
INFO:     Application startup complete.
```

#### 6.4 Verify Backend is Running

Open browser or use curl:
```bash
# Health check
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

**API Documentation:**
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

---

### Step 7: Run Frontend (Development Mode)

#### 7.1 Open New Terminal Window

Keep backend running in the first terminal, open a new terminal for frontend.

#### 7.2 Navigate to Frontend
```bash
cd F:\Tiramai\frontend
```

#### 7.3 Start Development Server
```bash
npm run dev
```

**Expected Output:**
```
  VITE v5.0.4  ready in xxx ms

  ➜  Local:   http://localhost:5173/
  ➜  Network: use --host to expose
  ➜  press h + enter to show help
```

**Note:** Vite uses port 5173 by default, but we configured it to use 3000 in `vite.config.ts`.

#### 7.4 Verify Frontend is Running

Open browser:
```
http://localhost:3000
```

You should see the Tiramai RAG System homepage.

---

## File Locations Summary

### Backend Files
```
backend/
├── .venv/                    ← Virtual environment (created by uv)
├── .env                      ← Environment variables (YOU CREATE THIS)
├── app/                      ← Application code
├── pyproject.toml            ← Project configuration
├── uv.lock                   ← Lock file (auto-generated)
└── migrations/               ← Database migrations
```

### Frontend Files
```
frontend/
├── node_modules/             ← Dependencies (created by npm install)
├── .env                      ← Environment variables (optional)
├── src/                      ← Source code
├── package.json              ← Project configuration
├── package-lock.json         ← Lock file (auto-generated)
└── vite.config.ts           ← Vite configuration
```

### Root Files
```
tiramai-rag/
├── .env.example              ← Example env file (reference)
├── .gitignore                ← Git ignore rules
├── .dockerignore             ← Docker ignore rules
├── docker-compose.yml        ← Docker orchestration
└── docs/                     ← Documentation
```

---

## Common Commands Reference

### Backend Commands
```bash
# Activate virtual environment
cd backend
.\.venv\Scripts\Activate.ps1  # Windows PowerShell

# Run backend
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload

# Install new dependency
uv add package-name

# Update dependencies
uv sync

# Deactivate virtual environment
deactivate
```

### Frontend Commands
```bash
# Install dependencies
cd frontend
npm install

# Run development server
npm run dev

# Build for production
npm run build

# Preview production build
npm run preview
```

### Docker Commands
```bash
# Start PostgreSQL only
docker-compose up -d postgres

# Start all services
docker-compose up -d

# Stop services
docker-compose down

# View logs
docker-compose logs -f postgres

# Stop and remove volumes (clean slate)
docker-compose down -v
```

---

## Troubleshooting

### Backend Issues

**Issue: Module not found errors**
- Ensure virtual environment is activated
- Run `uv sync` again
- Check that you're in the `backend/` directory

**Issue: Database connection errors**
- Ensure PostgreSQL is running: `docker-compose ps`
- Check `DATABASE_URL` in `backend/.env`
- Verify database credentials match docker-compose.yml

**Issue: Port 8000 already in use**
- Change port in command: `uvicorn app.main:app --port 8001`
- Or kill process using port 8000

### Frontend Issues

**Issue: Port 3000 already in use**
- Vite will automatically use next available port
- Or change port in `vite.config.ts`

**Issue: Cannot connect to backend API**
- Ensure backend is running on port 8000
- Check `VITE_API_URL` in `frontend/.env` or `vite.config.ts` proxy settings
- Check CORS settings in backend

**Issue: Module not found errors**
- Run `npm install` again
- Delete `node_modules/` and `package-lock.json`, then `npm install`

### Database Issues

**Issue: pgvector extension not found**
- Ensure you're using `pgvector/pgvector:pg15` image
- Check `backend/migrations/init.sql` is mounted correctly
- Restart PostgreSQL: `docker-compose restart postgres`

---

## Next Steps

After completing setup:
1. ✅ Backend running on http://localhost:8000
2. ✅ Frontend running on http://localhost:3000
3. ✅ PostgreSQL running with pgvector
4. ✅ Health check endpoint working

You're ready to proceed with **Phase 2: RAG Ingestion Pipeline**!

