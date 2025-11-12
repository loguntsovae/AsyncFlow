#!/usr/bin/env bash
# Simple demo script for AsyncFlow portfolio presentation
# Usage: ./scripts/demo.sh [up]
# If 'up' is passed, the script will run `docker compose up -d --build` before the demo.

set -euo pipefail

ROOT_DIR="$(cd "$(dirname "$0")/.." && pwd)"
GATEWAY_URL="http://localhost:9000"

if [ "${1:-}" = "up" ]; then
  echo "Starting services with Docker Compose..."
  (cd "$ROOT_DIR" && docker compose up -d --build)
  echo "Waiting for services to become ready (10s)..."
  sleep 10
fi

echo "Gateway health:" 
curl -sS "$GATEWAY_URL/health" | jq . || true

echo
echo "Creating a sample order..."
CREATE_RESP=$(curl -sS -X POST "$GATEWAY_URL/api/v1/orders" \
  -H "Content-Type: application/json" \
  -d '{"user_id": 1, "amount": 19.99}')

echo "$CREATE_RESP" | jq .

echo
echo "Waiting a few seconds for the Billing consumer to process the event..."
sleep 5

echo
echo "List orders (latest):"
curl -sS "$GATEWAY_URL/api/v1/orders" | jq .

echo
echo "Done."
