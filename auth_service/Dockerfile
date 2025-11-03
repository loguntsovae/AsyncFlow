FROM python:3.11-slim

WORKDIR /app

# Runtime Python settings
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PYTHONPATH=/app/src

# Install uv for faster package installation
RUN pip install --no-cache-dir uv==0.4.20

# Copy dependency definitions and project files
COPY pyproject.toml ./
COPY alembic.ini ./
COPY README.md ./
COPY migrations/ ./migrations/
COPY src/ ./src/

# Install dependencies directly from pyproject.toml using uv
RUN uv pip install --system --no-cache --compile .

# Default port (can be overridden)
ENV AUTH_SERVICE_PORT=9003

# Expose the port
EXPOSE ${AUTH_SERVICE_PORT}

# Copy entrypoint script
COPY docker-entrypoint.sh /usr/local/bin/docker-entrypoint.sh
RUN chmod +x /usr/local/bin/docker-entrypoint.sh

# Install tools used by entrypoint and healthcheck
RUN apt-get update \
     && apt-get install -y --no-install-recommends \
         netcat-openbsd \
         wget \
         curl \
         ca-certificates \
     && rm -rf /var/lib/apt/lists/*

# Health check
HEALTHCHECK --interval=30s --timeout=5s --start-period=15s --retries=3 \
    CMD wget -qO- http://localhost:${AUTH_SERVICE_PORT}/health >/dev/null || exit 1

# Run the application
ENTRYPOINT ["docker-entrypoint.sh"]
CMD ["uvicorn", "src.main:app"]