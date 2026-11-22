# ==============================================================================
# JurisAI Backend Dockerfile
# Multi-Agent Constraint-Aware Legal Reasoning Engine
# ==============================================================================
FROM python:3.11-slim

# Avoid buffering and bytecode generation
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_NO_CACHE_DIR=1

WORKDIR /app

# Install system runtime dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copy dependencies first for Docker caching
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code and metadata
COPY backend/ ./backend/
COPY observability/ ./observability/
COPY legal_rag_pipeline.py .
COPY multi_agent_workflow.py .
COPY vector_query_service.py .
COPY reanalysis_system.py .
COPY section_metadata.json .
COPY act_metadata.json .
COPY judgment_metadata.json .
COPY judgment_base_metadata.json .
COPY judgment_enriched_metadata.json .

# Create persistent storage directories
RUN mkdir -p /app/chroma_db /app/logs /app/data

# Default environment variables
ENV HOST=0.0.0.0 \
    PORT=8000 \
    CHROMA_PERSIST_DIR=/app/chroma_db \
    OLLAMA_BASE_URL=http://ollama:11434 \
    OLLAMA_MODEL=qwen2.5:0.5b

EXPOSE 8000

# Health check
HEALTHCHECK --interval=20s --timeout=5s --start-period=15s --retries=3 \
    CMD curl -f http://localhost:8000/metrics || exit 1

# Launch FastAPI with uvicorn
CMD ["python", "-m", "uvicorn", "backend.main:app", "--host", "0.0.0.0", "--port", "8000"]
