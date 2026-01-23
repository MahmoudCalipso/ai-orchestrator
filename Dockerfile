# =============================================================================
# IA-ORCHESTRATOR 2026 - ENTERPRISE DOCKER IMAGE
# Multi-stage build for security, performance, and automatic model downloading
# =============================================================================

# =============================================================================
# Stage 1: Builder - Compile dependencies
# =============================================================================
FROM python:3.11-slim AS builder

LABEL maintainer="Mahmoud Calipso <support@ia-orch.example.com>"
LABEL description="IA-Orchestrator 2026 - Enterprise AI Platform"
LABEL version="2.0.0"

WORKDIR /build

# Install build dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    cmake \
    git \
    curl \
    wget \
    libpq-dev \
    libssl-dev \
    pkg-config \
    && rm -rf /var/lib/apt/lists/*

# Copy and install Python dependencies
COPY requirements.txt .
RUN pip install --user --no-cache-dir --upgrade pip setuptools wheel && \
    pip install --user --no-cache-dir -r requirements.txt

# =============================================================================
# Stage 2: Runtime - Minimal secure image
# =============================================================================
FROM python:3.11-slim

WORKDIR /app

# Install runtime dependencies and security tools
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    wget \
    ca-certificates \
    libpq5 \
    git \
    tini \
    && rm -rf /var/lib/apt/lists/* \
    && apt-get clean

# Copy Python packages from builder
COPY --from=builder /root/.local /root/.local
ENV PATH=/root/.local/bin:$PATH

# Create non-root user for security
RUN groupadd -r orchestrator && \
    useradd -r -g orchestrator -u 1000 -m -s /bin/bash orchestrator && \
    mkdir -p /app /app/models /app/logs /app/cache /app/data && \
    chown -R orchestrator:orchestrator /app

# Copy application code
COPY --chown=orchestrator:orchestrator . .

# Copy model download script
COPY --chown=orchestrator:orchestrator scripts/download_models.sh /app/scripts/
RUN chmod +x /app/scripts/download_models.sh

# Security: Remove unnecessary files
RUN find /app -name "*.pyc" -delete && \
    find /app -name "__pycache__" -type d -exec rm -rf {} + 2>/dev/null || true && \
    rm -rf /app/setup.ps1 /app/start.ps1 /app/download_models.ps1 /app/.git

# Switch to non-root user
USER orchestrator

# Environment variables for security and performance
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PYTHONHASHSEED=random \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1 \
    MALLOC_ARENA_MAX=2 \
    MALLOC_MMAP_THRESHOLD_=131072 \
    MALLOC_TRIM_THRESHOLD_=131072 \
    MALLOC_TOP_PAD_=131072 \
    MALLOC_MMAP_MAX_=65536

# Expose port
EXPOSE 8000

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=60s --retries=3 \
    CMD curl -f http://localhost:8000/health || exit 1

# Use tini as init system for proper signal handling
ENTRYPOINT ["/usr/bin/tini", "--"]

# Start application with uvicorn for production
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000", "--workers", "4", "--loop", "uvloop", "--http", "httptools"]
