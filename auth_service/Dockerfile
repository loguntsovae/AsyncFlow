FROM python:3.11-slim

WORKDIR /app

# Install uv for faster package installation
RUN pip install --no-cache-dir uv==0.4.20

# Copy project files
COPY pyproject.toml ./
COPY alembic.ini ./
COPY migrations/ ./migrations/
COPY src/ ./src/

# Install dependencies
RUN uv pip install --system --no-cache --compile .

# Default port (can be overridden)
ENV AUTH_SERVICE_PORT=9003

# Expose the port
EXPOSE ${AUTH_SERVICE_PORT}

# Create startup script using separate RUN commands for better Docker layer caching
RUN echo '#!/bin/sh' > /app/start.sh && \
    echo 'set -e' >> /app/start.sh && \
    echo 'echo "Waiting for database..."' >> /app/start.sh && \
    echo 'while ! nc -z ${POSTGRES_HOST:-postgres} ${POSTGRES_PORT:-5432}; do sleep 1; done' >> /app/start.sh && \
    echo 'echo "Database is ready!"' >> /app/start.sh && \
    echo 'echo "Running migrations..."' >> /app/start.sh && \
    echo 'alembic upgrade head' >> /app/start.sh && \
    echo 'echo "Starting Auth Service on port ${AUTH_SERVICE_PORT}..."' >> /app/start.sh && \
    echo 'exec uvicorn src.main:app --host 0.0.0.0 --port ${AUTH_SERVICE_PORT}' >> /app/start.sh && \
    chmod +x /app/start.sh

# Install netcat for health checks
RUN apt-get update && apt-get install -y netcat-openbsd && rm -rf /var/lib/apt/lists/*

# Run the application
CMD ["/app/start.sh"]