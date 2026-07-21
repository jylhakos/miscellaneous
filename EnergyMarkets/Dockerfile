# Multi-stage Docker build for FastAPI Power Trading Backend
# Optimized for production deployment with minimal image size

# ============================================================================
# Stage 1: Builder - Install dependencies
# ============================================================================
FROM python:3.11-slim as builder

WORKDIR /build

# Install system dependencies required for building Python packages
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements and install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir --user -r requirements.txt

# ============================================================================
# Stage 2: Runtime - Minimal production image
# ============================================================================
FROM python:3.11-slim

WORKDIR /app

# Install only runtime dependencies
RUN apt-get update && apt-get install -y \
    libpq5 \
    && rm -rf /var/lib/apt/lists/*

# Copy Python packages from builder stage
COPY --from=builder /root/.local /root/.local

# Ensure Python packages are in PATH
ENV PATH=/root/.local/bin:$PATH

# Copy application code
COPY scripts/ /app/scripts/
COPY .env.example /app/.env.example

# Create data directory for outputs
RUN mkdir -p /app/data

# Set Python to run in unbuffered mode for better logging
ENV PYTHONUNBUFFERED=1

# Expose FastAPI port
EXPOSE 8000

# Health check endpoint
HEALTHCHECK --interval=30s --timeout=10s --start-period=40s --retries=3 \
    CMD python -c "import requests; requests.get('http://localhost:8000/api/v1/health')"

# Default command: Run FastAPI with Uvicorn
CMD ["python", "-m", "uvicorn", "scripts.main:app", "--host", "0.0.0.0", "--port", "8000"]
