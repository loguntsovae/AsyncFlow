FROM python:3.11-slim

WORKDIR /app

# Install poetry
RUN pip install poetry

# Copy project files
COPY pyproject.toml poetry.lock* ./
COPY alembic.ini ./
COPY migrations/ ./migrations/
COPY src/ ./src/

# Install dependencies
RUN poetry config virtualenvs.create false \
    && poetry install --no-dev --no-interaction --no-ansi

# Expose the port
EXPOSE 9003

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