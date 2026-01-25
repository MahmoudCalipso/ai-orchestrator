# =============================================================================
# IA-ORCHESTRATOR 2026 - PRODUCTION DOCKER IMAGE
# Multi-stage build for optimized image size and security
# =============================================================================

# =============================================================================
# Stage 1: Builder - Compile Python dependencies
# =============================================================================
FROM python:3.11-slim AS builder

LABEL maintainer="Mahmoud Calipso <support@ia-orch.example.com>"
LABEL description="IA-Orchestrator 2026 - Enterprise AI Platform"
LABEL version="2.0.0"

WORKDIR /build

# Install build dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    libpq-dev \
    libssl-dev \
    pkg-config \
    && rm -rf /var/lib/apt/lists/*

# Copy and install Python dependencies
COPY requirements.txt .
RUN pip install --user --no-cache-dir --upgrade pip setuptools wheel && \
    pip install --user --no-cache-dir -r requirements.txt

# =============================================================================
# Stage 2: Runtime - Production image
# =============================================================================
FROM python:3.11-slim

WORKDIR /app

# Install runtime dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    wget \
    ca-certificates \
    libpq5 \
    git \
    tini \
    bash \
    && rm -rf /var/lib/apt/lists/* \
    && apt-get clean

# Copy Python packages from builder
COPY --from=builder /root/.local /root/.local
ENV PATH=/root/.local/bin:$PATH

# Create non-root user and directories
RUN groupadd -r orchestrator && \
    useradd -r -g orchestrator -u 1000 -m -s /bin/bash orchestrator && \
    mkdir -p /app/models /app/logs /app/cache /app/data /app/storage /app/scripts && \
    chown -R orchestrator:orchestrator /app

# Copy application code (excluding large dirs via .dockerignore)
COPY --chown=orchestrator:orchestrator . .

# Copy model download script (only the one used by docker-compose)
COPY --chown=orchestrator:orchestrator scripts/download_models.sh /app/scripts/
RUN chmod +x /app/scripts/download_models.sh

# Security: Remove Windows-specific files
RUN rm -f /app/download_models.ps1

# Security: Clean up Python cache
RUN find /app -name "*.pyc" -delete && \
    find /app -name "__pycache__" -type d -exec rm -rf {} + 2>/dev/null || true

# Switch to non-root user
USER orchestrator

# Environment variables
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PYTHONHASHSEED=random \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

# Expose port
EXPOSE 8000

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=60s --retries=3 \
    CMD curl -f http://localhost:8000/health || exit 1

# Use tini as init system for proper signal handling
ENTRYPOINT ["/usr/bin/tini", "--"]

# Start application with uvicorn
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000", "--workers", "4"]
