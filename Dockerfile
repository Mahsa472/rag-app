# ============================================================================
# Stage 1: Build stage - install dependencies that need compilation
# ============================================================================
FROM python:3.11-slim as builder

# Set working directory
WORKDIR /app

# Install only build dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    gcc \
    g++ \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements file
COPY requirements.txt .

# Install Python dependencies with no cache
# Note: torch CPU version requires the extra index URL
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir --extra-index-url https://download.pytorch.org/whl/cpu \
    -r requirements.txt

# ============================================================================
# Stage 2: Runtime stage - minimal image with only runtime dependencies
# ============================================================================
FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Environment: avoid creating .pyc and enable unbuffered logs
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PYTHONPATH=/app/src \
    HF_HOME=/app/cache \
    DATA_DIR=/app/data/pdfs \
    CHROMA_DIR=/app/data/chroma_db \
    EMBEDDING_MODEL=sentence-transformers/all-MiniLM-L6-v2 \
    TOP_K=5 \
    CHUNK_SIZE=800 \
    CHUNK_OVERLAP=200

# Install only runtime system dependencies (minimal)
# ChromaDB and PyPDF2 may need some libraries, but no build tools
RUN apt-get update && apt-get install -y --no-install-recommends \
    libgomp1 \
    && rm -rf /var/lib/apt/lists/* \
    && apt-get clean

# Copy Python packages from builder stage
COPY --from=builder /usr/local/lib/python3.11/site-packages /usr/local/lib/python3.11/site-packages
COPY --from=builder /usr/local/bin /usr/local/bin

# Copy application source code
COPY src/ ./src/

# Create data directories
RUN mkdir -p /app/data/pdfs /app/data/chroma_db /app/cache

# Pre-download and cache the embedding model (smaller model for faster startup)
RUN python -c "from sentence_transformers import SentenceTransformer; SentenceTransformer('sentence-transformers/all-MiniLM-L6-v2')" && \
    find /app/cache -type f -name "*.tmp" -delete 2>/dev/null || true

# Remove unnecessary files to reduce image size
RUN find /usr/local/lib/python3.11/site-packages -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true && \
    find /usr/local/lib/python3.11/site-packages -type f -name "*.pyc" -delete 2>/dev/null || true && \
    find /usr/local/lib/python3.11/site-packages -type f -name "*.pyo" -delete 2>/dev/null || true && \
    find /usr/local/lib/python3.11/site-packages -type d -name "tests" -exec rm -rf {} + 2>/dev/null || true && \
    find /usr/local/lib/python3.11/site-packages -type d -name "test" -exec rm -rf {} + 2>/dev/null || true && \
    find /usr/local/lib/python3.11/site-packages -type f -name "*.md" -delete 2>/dev/null || true && \
    find /usr/local/lib/python3.11/site-packages -type f -name "*.txt" -path "*/test*" -delete 2>/dev/null || true && \
    rm -rf /root/.cache/pip 2>/dev/null || true && \
    rm -rf /tmp/* 2>/dev/null || true

# Expose the port Flask runs on
EXPOSE 8000

# Run the Flask application
CMD ["python", "src/app_rag.py"]

