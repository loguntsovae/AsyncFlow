# ─────────────────────────────────────────────
#   Stage 1 — Builder (установка зависимостей)
# ─────────────────────────────────────────────
FROM python:3.12.6-slim-bookworm AS builder

# Устанавливаем системные пакеты, необходимые для сборки зависимостей (например, asyncpg)
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential curl ca-certificates \
 && rm -rf /var/lib/apt/lists/*

# Устанавливаем uv (быстрая альтернатива pip/poetry)
RUN pip install --no-cache-dir uv==0.4.20

WORKDIR /build

# Копируем только pyproject.toml — для кэширования зависимостей
COPY pyproject.toml ./

# Устанавливаем зависимости в системный Python
RUN uv pip install --system --no-cache --compile .


# ─────────────────────────────────────────────
#   Stage 2 — Runtime
# ─────────────────────────────────────────────
FROM python:3.12.6-slim-bookworm AS runtime

RUN useradd --create-home --shell /bin/bash appuser

WORKDIR /app
RUN rm -rf /app/.venv
COPY --chown=appuser:appuser . .

# ⬇️ добавляем копирование bin
COPY --from=builder /usr/local/lib/python3.12 /usr/local/lib/python3.12
COPY --from=builder /usr/local/bin /usr/local/bin

USER appuser

ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    UV_SYSTEM_PYTHON=1 \
    PYTHONPATH=/app \
    ORDER_SERVICE_PORT=9001

EXPOSE ${ORDER_SERVICE_PORT}

HEALTHCHECK --interval=30s --timeout=5s --start-period=20s --retries=3 \
  CMD curl -fsS http://localhost:${ORDER_SERVICE_PORT}/health || exit 1

CMD ["uvicorn", "src.main:app", "--host", "0.0.0.0", "--port", "${ORDER_SERVICE_PORT}"]