#!/bin/sh
set -euo pipefail

# Defaults (can be overridden by env)
: "${POSTGRES_HOST:=postgres}"
: "${POSTGRES_PORT:=5432}"
: "${AUTH_SERVICE_PORT:=9003}"

log() {
  printf "[auth-entrypoint] %s\n" "$*"
}

wait_for_port() {
  host="$1"; port="$2"; name="${3:-service}"
  log "Waiting for $name at ${host}:${port}..."
  until nc -z "$host" "$port"; do
    sleep 1
  done
  log "$name is available"
}

# Wait for Postgres
wait_for_port "$POSTGRES_HOST" "$POSTGRES_PORT" "Postgres"

# Run migrations
log "Running Alembic migrations..."
# Ensure alembic uses the bundled alembic.ini in /app
cd /app
alembic upgrade head
log "Migrations complete"

# Exec the application
log "Starting Auth Service on port ${AUTH_SERVICE_PORT}"
if [ "$#" -gt 0 ] && [ "$1" = "uvicorn" ]; then
  shift
  exec uvicorn "$@" --host 0.0.0.0 --port "${AUTH_SERVICE_PORT}"
else
  exec "$@"
fi
