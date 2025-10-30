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

alembic upgrade head\n\
# Create startup script
RUN cat <<'EOF' > /app/start.sh
#!/bin/sh
# Wait for database
while !</dev/tcp/$POSTGRES_HOST/$POSTGRES_PORT; do sleep 1; done;

# Run migrations
alembic upgrade head

# Start application with uvicorn using AUTH_SERVICE_PORT
exec uvicorn src.main:app --host 0.0.0.0 --port ${AUTH_SERVICE_PORT}
EOF

RUN chmod +x /app/start.sh

# Run the application
CMD ["/app/start.sh"]