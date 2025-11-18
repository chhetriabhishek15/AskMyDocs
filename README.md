# Tiramai RAG System

🚀 Production-ready Retrieval-Augmented Generation system for document intelligence and AI-powered Q&A.

## Overview

Tiramai RAG is a complete RAG platform that enables you to:
- Upload and process documents (PDF, DOCX, ZIP, images)
- Perform semantic search across your document library
- Chat with your documents using AI-powered retrieval

## Features

- 📄 **Multi-format Support**: PDF, DOCX, DOC, ZIP, TXT, MD
- 🔍 **Hybrid Chunking**: Advanced document chunking with Docling
- 💾 **Vector Search**: PostgreSQL + pgvector for efficient similarity search
- 🧠 **Conversational Memory**: Persistent memory with Memori
- 🤖 **LLM Integration**: Google Gemini API for intelligent responses
- 🎨 **Modern UI**: Clean React interface with drag-and-drop upload
- ⚡ **High Performance**: Fully async FastAPI backend
- 🐳 **Docker Ready**: Complete Docker Compose setup

## Tech Stack

- **Frontend**: React 18 + TypeScript + Tailwind CSS + React Query
- **Backend**: FastAPI + SQLAlchemy (async) + Pydantic
- **Document Processing**: [Docling](https://docling-project.github.io/docling/examples/)
- **Memory**: [Memori](https://github.com/GibsonAI/Memori)
- **Vector DB**: PostgreSQL 15 + pgvector
- **LLM**: Google Gemini API
- **Embeddings**: sentence-transformers/all-MiniLM-L6-v2
- **Package Manager**: [uv](https://docs.astral.sh/uv/getting-started/installation/)
- **Orchestration**: Docker + Docker Compose

## Quick Start

### Option 1: Docker Compose (Recommended) 🐳

The easiest way to run the entire application:

1. **Create environment files** (see [SETUP.md](SETUP.md) for details)
   - Root `.env` - Docker Compose variables
   - `backend/.env` - Application configuration

2. **Start all services**
   ```bash
   docker-compose up -d
   ```

3. **Access the application:**
   - Frontend: http://localhost:3000
   - Backend API: http://localhost:8000
   - API Docs: http://localhost:8000/docs

**See [SETUP.md](SETUP.md) for complete Docker Compose setup guide.**

### Option 2: Local Development

For local development (backend/frontend outside Docker):

1. **Start PostgreSQL with Docker**
   ```bash
   docker-compose up -d postgres
   ```

2. **Run backend** (see [docs/setup-guide.md](docs/setup-guide.md))
   ```bash
   cd backend
   uv venv && uv sync
   uv run uvicorn app.main:app --reload
   ```

3. **Run frontend**
   ```bash
   cd frontend
   npm install
   npm run dev
   ```

**Note:** When running locally, use `localhost` instead of `postgres` in `DATABASE_URL`.

## Environment Files

⚠️ **Important**: This project uses **two `.env` files**:

1. **Root `.env`** - For Docker Compose (database credentials, ports)
2. **`backend/.env`** - For FastAPI application (API keys, app config)

See [ENV_FILES_GUIDE.md](ENV_FILES_GUIDE.md) for detailed explanation.

## Project Structure

```
tiramai-rag/
├── frontend/          # React frontend application
├── backend/           # FastAPI backend application
│   └── .env          # Backend application config
├── docs/              # Documentation
├── docker-compose.yml # Docker orchestration
├── .env              # Docker Compose config (root)
└── .cursor/           # Cursor IDE rules
```

## Documentation

- **[SETUP.md](SETUP.md)** - Quick setup guide (Docker Compose + Local)
- [Docker Setup Guide](docs/docker-setup.md) - Complete Docker Compose guide
- [Detailed Setup Guide](docs/setup-guide.md) - Local development setup
- [Architecture](docs/architecture.md) - System architecture
- [API Design](docs/api-design.md) - API endpoints
- [RAG Design](docs/rag-design.md) - RAG pipeline design

## Development

See [docs/plan.md](docs/plan.md) for detailed development plan and architecture.

## License

[Your License Here]
