# Tiramai RAG - Quick Setup Guide

## Prerequisites
- **Docker Desktop** installed and running
- **Docker Compose** (included with Docker Desktop)
- **Git** (for cloning the repository)

## 🚀 Quick Start with Docker Compose (Recommended)

### Step 1: Clone/Verify Project
```bash
cd F:\Tiramai
```

### Step 2: Create Environment Files

#### 2.1 Create Root `.env` File
Create `.env` in the project root (`F:\Tiramai\.env`):

```env
# PostgreSQL Configuration (for Docker Compose)
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

#### 2.2 Create Backend `.env` File
Create `backend/.env`:

```env
# Database (use 'postgres' hostname when running in Docker, 'localhost' when running locally)
DATABASE_URL=postgresql+asyncpg://tiramai_user:tiramai_password@postgres:5432/tiramai_db

# LLM Configuration
GEMINI_API_KEY=your_gemini_api_key_here
GEMINI_MODEL=gemini-pro

# Memori Configuration
MEMORI_DATABASE_CONNECTION=postgresql://tiramai_user:tiramai_password@postgres:5432/tiramai_db
MEMORI_NAMESPACE=production

# Application
DEBUG=true
LOG_LEVEL=INFO

# CORS
CORS_ORIGINS=http://localhost:3000,http://localhost:5173

# Embedding Model
EMBEDDING_MODEL=sentence-transformers/all-MiniLM-L6-v2
EMBEDDING_DIMENSION=384
```

**Important:** Replace `your_gemini_api_key_here` with your actual Gemini API key.

### Step 3: Start All Services with Docker Compose

```bash
# From project root (F:\Tiramai)
docker-compose up -d
```

This will:
- ✅ Build backend and frontend Docker images
- ✅ Start PostgreSQL with pgvector
- ✅ Start backend service
- ✅ Start frontend service
- ✅ Wait for PostgreSQL to be healthy before starting backend

### Step 4: Verify Services are Running

```bash
# Check all services
docker-compose ps

# View logs
docker-compose logs -f

# Check specific service logs
docker-compose logs -f backend
docker-compose logs -f frontend
docker-compose logs -f postgres
```

### Step 5: Access the Application

- **Frontend**: http://localhost:3000
- **Backend API**: http://localhost:8000
- **API Docs**: http://localhost:8000/docs
- **Health Check**: http://localhost:8000/api/v1/health

### Step 6: Stop Services

```bash
# Stop all services (keeps data)
docker-compose down

# Stop and remove volumes (clean slate - deletes database data)
docker-compose down -v
```

---

## 🔧 Development Setup (Local - Without Docker)

If you prefer to run backend/frontend locally while using Docker only for PostgreSQL:

### Prerequisites
- Python 3.11+, Node.js 20+, Docker, uv

### 1. Backend Setup
```bash
cd backend
uv venv
uv sync
.\.venv\Scripts\Activate.ps1  # Windows PowerShell
# Create backend/.env (use 'localhost' instead of 'postgres' in DATABASE_URL)
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

### 2. Frontend Setup
```bash
cd frontend
npm install
npm run dev
```

### 3. Database Setup (Docker)
```bash
# From project root
docker-compose up -d postgres
```

**Note:** When running locally, use `localhost` in `DATABASE_URL` instead of `postgres`.

---

## 📁 File Locations

### Docker Setup
- **Root `.env`**: `F:\Tiramai\.env` (Docker Compose variables)
- **Backend `.env`**: `backend/.env` (Application configuration)
- **Docker volumes**: Managed by Docker (postgres_data, uploads_data)

### Local Development
- **Backend .venv**: `backend/.venv/`
- **Backend .env**: `backend/.env` (use `localhost` in DATABASE_URL)
- **Frontend node_modules**: `frontend/node_modules/`

---

## 🐛 Troubleshooting

### Docker Issues

**Issue: Services won't start**
```bash
# Check Docker Desktop is running
# View detailed logs
docker-compose logs

# Rebuild images
docker-compose build --no-cache
docker-compose up -d
```

**Issue: Port already in use**
- Change ports in root `.env` file
- Or stop the service using the port

**Issue: Database connection errors**
- Ensure PostgreSQL container is healthy: `docker-compose ps`
- Check credentials match in root `.env` and `backend/.env`
- Verify `DATABASE_URL` uses `postgres` hostname (when in Docker) or `localhost` (when local)

**Issue: Frontend can't connect to backend**
- Check `VITE_API_URL` in root `.env`
- Verify backend is running: `curl http://localhost:8000/api/v1/health`
- Check CORS settings in `backend/.env`

### Local Development Issues

See `docs/setup-guide.md` for detailed troubleshooting.

---

## 📚 Additional Documentation

- **Detailed Setup**: `docs/setup-guide.md`
- **Architecture**: `docs/architecture.md`
- **API Design**: `docs/api-design.md`
- **RAG Design**: `docs/rag-design.md`

---

## ✅ Verification Checklist

After setup, verify:

- [ ] PostgreSQL container is running (`docker-compose ps`)
- [ ] Backend health check works (`curl http://localhost:8000/api/v1/health`)
- [ ] Frontend loads at http://localhost:3000
- [ ] API docs accessible at http://localhost:8000/docs
- [ ] Database connection test passes (`cd backend && uv run python scripts/test_db_connection.py`)

**You're ready to proceed with Phase 2: RAG Ingestion Pipeline!** 🎉

