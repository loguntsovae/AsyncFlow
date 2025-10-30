#!/bin/sh
set -e

# Create log directory if it doesn't exist (fallback to /app/logs)
LOG_DIR_PATH="${LOG_DIR:-${APP_HOME:-/app}/logs}"
mkdir -p "$LOG_DIR_PATH"

# Wait for dependent services if needed
wait_for_service() {
    host="$1"
    port="$2"
    echo "Waiting for $host:$port..."
    while ! nc -z "$host" "$port"; do
        sleep 1
    done
    echo "$host:$port is available"
}

# Example: Wait for auth service
if [ -n "$AUTH_SERVICE_HOST" ] && [ -n "$AUTH_SERVICE_PORT" ]; then
    wait_for_service "$AUTH_SERVICE_HOST" "$AUTH_SERVICE_PORT"
fi

# Run the application
exec "$@"