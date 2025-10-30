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

# Create startup script
RUN echo '#!/bin/sh\n\
# Wait for database\n\
while !</dev/tcp/$POSTGRES_HOST/$POSTGRES_PORT; do sleep 1; done;\n\
\n\
# Run migrations\n\
alembic upgrade head\n\
\n\
# Start application\n\
python -m src.main' > /app/start.sh \
    && chmod +x /app/start.sh

# Run the application
CMD ["/app/start.sh"]