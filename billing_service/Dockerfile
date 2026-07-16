# ─────────────────────────────────────────────
#   Stage 1 — Builder (dependency install)
# ─────────────────────────────────────────────
FROM python:3.12.6-slim-bookworm AS builder

RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential curl ca-certificates \
 && rm -rf /var/lib/apt/lists/*

RUN pip install --no-cache-dir uv==0.4.20

WORKDIR /build

COPY pyproject.toml ./

RUN uv pip install --system --no-cache --compile .

# ─────────────────────────────────────────────
#   Stage 2 — Runtime
# ─────────────────────────────────────────────
FROM python:3.12.6-slim-bookworm AS runtime

RUN useradd --create-home --shell /bin/bash appuser

WORKDIR /app
COPY --chown=appuser:appuser . .

COPY --from=builder /usr/local/lib/python3.12 /usr/local/lib/python3.12
COPY --from=builder /usr/local/bin /usr/local/bin

USER appuser

ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PYTHONPATH=/app

# Billing is a queue consumer — no HTTP port; healthcheck is process liveness
HEALTHCHECK --interval=30s --timeout=5s --start-period=15s --retries=3 \
  CMD pgrep -f "src.main" || exit 1

CMD ["python", "-m", "src.main"]
