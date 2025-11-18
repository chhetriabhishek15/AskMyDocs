#############################
# Stage 1: Dependencies only
#############################
FROM python:3.11-slim AS builder

WORKDIR /app

# Prevent interactive prompts during install
ENV DEBIAN_FRONTEND=noninteractive

# Install system build dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    g++ \
    curl \
    libffi-dev \
    && rm -rf /var/lib/apt/lists/*

# Copy only requirement file (keeps caching efficient)
COPY requirements.txt .

# Upgrade pip + install dependencies into venv
RUN python -m venv /opt/venv
ENV PATH=/opt/venv/bin:$PATH

# Faster downloads + no pip cache
RUN pip install --upgrade pip setuptools wheel \
    && pip install --no-cache-dir -r requirements.txt


#############################
# Stage 2: Runtime image
#############################
FROM python:3.11-slim

WORKDIR /app

# Install minimal system dependencies for runtime
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    libgomp1 \
    && rm -rf /var/lib/apt/lists/*

# Copy virtual environment from builder
COPY --from=builder /opt/venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

# Copy only application code
COPY app ./app
COPY pyproject.toml .
COPY migrations ./migrations

# Create uploads folder
RUN mkdir -p /app/uploads

# Non-root user (best practice)
RUN useradd -m appuser
USER appuser

EXPOSE 8000

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8000/api/v1/health || exit 1

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
