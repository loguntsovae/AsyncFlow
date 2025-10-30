# syntax=docker/dockerfile:1
FROM python:3.11-slim as builder

# Build arguments
ARG APP_USER=appuser
ARG APP_GROUP=appgroup
ARG APP_HOME=/app

# Prevent Python from writing pyc files and from buffering stdout/stderr
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Set work directory
WORKDIR ${APP_HOME}

# Install system dependencies and create user
RUN apt-get update \
    && apt-get install -y --no-install-recommends \
        curl \
        build-essential \
    && rm -rf /var/lib/apt/lists/* \
    && groupadd -r ${APP_GROUP} \
    && useradd -r -g ${APP_GROUP} -d ${APP_HOME} ${APP_USER} \
    && mkdir -p ${APP_HOME}/logs \
    && chown -R ${APP_USER}:${APP_GROUP} ${APP_HOME}

# Install poetry
RUN curl -sSL https://install.python-poetry.org | python3 -

# Copy dependency files
COPY --chown=${APP_USER}:${APP_GROUP} pyproject.toml poetry.lock* ./

# Install dependencies
RUN poetry config virtualenvs.create false \
    && poetry install --no-dev --no-interaction --no-ansi

# Copy application code
COPY --chown=${APP_USER}:${APP_GROUP} src/ ./src/

# Create a non-root user to run the application
USER ${APP_USER}

# Create volume for logs
VOLUME ["${APP_HOME}/logs"]

# Expose the port
EXPOSE 9000

# Health check
HEALTHCHECK --interval=30s --timeout=3s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8000/health || exit 1

# Set entry point script
COPY --chown=${APP_USER}:${APP_GROUP} docker-entrypoint.sh /usr/local/bin/
RUN chmod +x /usr/local/bin/docker-entrypoint.sh

# Set environment variables for the application
ENV APP_ENV=production \
    LOG_LEVEL=info \
    LOG_FORMAT=json \
    LOG_DIR=${APP_HOME}/logs

ENTRYPOINT ["docker-entrypoint.sh"]
CMD ["python", "-m", "src.main"]