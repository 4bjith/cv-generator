# ==============================================================================
# Multi-stage Production Dockerfile for AI CV Maker FastAPI Backend
# ==============================================================================

FROM python:3.14-slim AS builder

WORKDIR /app

# Install build dependencies if needed
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Install python dependencies in virtual environment
RUN python -m venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

COPY pyproject.toml .
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir .

# ==============================================================================
# Final Runtime Stage
# ==============================================================================
FROM python:3.14-slim AS runner

WORKDIR /app

# Create a dedicated non-root user and group
RUN groupadd -r appgroup && useradd -r -g appgroup -d /app appuser

# Copy installed packages from builder
COPY --from=builder /opt/venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

# Copy application source code
COPY --chown=appuser:appgroup app/ ./app
COPY --chown=appuser:appgroup pyproject.toml .

# Environment Defaults
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    HOST=0.0.0.0 \
    PORT=8000 \
    APP_ENV=production

# Switch to non-root user
USER appuser

EXPOSE 8000

# Container Healthcheck via built-in health liveness probe
HEALTHCHECK --interval=30s --timeout=5s --start-period=10s --retries=3 \
    CMD python -c "import urllib.request; urllib.request.urlopen('http://localhost:8000/api/v1/health/live').read()" || exit 1

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000", "--workers", "2", "--no-access-log"]
