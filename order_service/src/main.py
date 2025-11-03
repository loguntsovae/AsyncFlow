from __future__ import annotations
from fastapi.encoders import jsonable_encoder
import logging
from contextlib import asynccontextmanager
from typing import AsyncIterator, Optional, Sequence

import aio_pika
from fastapi import FastAPI
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.gzip import GZipMiddleware
from starlette.middleware.trustedhost import TrustedHostMiddleware
from starlette.requests import Request
from starlette.responses import JSONResponse

from src.settings import settings
from src.api import api_router


# ── ЛОГИРОВАНИЕ ────────────────────────────────────────────────────────────────
logger = logging.getLogger("asyncflow.order_service")
logging.basicConfig(
    level=getattr(logging, settings.log_level.upper(), logging.INFO),
    format="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
)


# ── LIFESPAN: подключение к RabbitMQ на старте, закрытие на остановке ──────────
@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncIterator[None]:
    """
    Инициализируем соединение с RabbitMQ (robust), канал и обменник.
    Кладём всё в app.state.*, чтобы использовать из зависимостей/роутеров.
    """
    # Build AMQP URL using the real secret value; mask in logs
    try:
        pass_value = settings.rabbitmq_pass.get_secret_value()  # pydantic SecretStr
    except AttributeError:
        pass_value = str(settings.rabbitmq_pass)

    amqp_url = (
        f"amqp://{settings.rabbitmq_user}:{pass_value}"
        f"@{settings.rabbitmq_host}:{settings.rabbitmq_port}/"
    )
    logger.info("Connecting to RabbitMQ: %s", amqp_url.replace(pass_value, "******"))

    connection: Optional[aio_pika.RobustConnection] = None
    channel: Optional[aio_pika.abc.AbstractChannel] = None
    exchange: Optional[aio_pika.abc.AbstractExchange] = None

    try:
        connection = await aio_pika.connect_robust(amqp_url)
        channel = await connection.channel()
        # durable topic exchange — чтобы переживал рестарты брокера
        exchange = await channel.declare_exchange(
            name=settings.amqp_exchange,
            type=aio_pika.ExchangeType.TOPIC,
            durable=True,
        )

        app.state.amqp_connection = connection
        app.state.amqp_channel = channel
        app.state.amqp_exchange = exchange

        logger.info("RabbitMQ connected. Exchange '%s' ready.", settings.amqp_exchange)
        yield

    finally:
        # Закрываем ресурсы аккуратно
        try:
            if channel and not channel.is_closed:
                await channel.close()
        except Exception as e:
            logger.warning("Channel close warning: %s", e)

        try:
            if connection and not connection.is_closed:
                await connection.close()
        except Exception as e:
            logger.warning("Connection close warning: %s", e)

        logger.info("RabbitMQ connection closed.")


# ── ПРИЛОЖЕНИЕ ────────────────────────────────────────────────────────────────
app = FastAPI(
    title="AsyncFlow - Order Service",
    version="0.1.0",
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan,
)


# ── MIDDLEWARE ────────────────────────────────────────────────────────────────
# GZip для ответов (экономит трафик)
app.add_middleware(GZipMiddleware, minimum_size=800)

# Trusted hosts (опционально — если хочешь ограничить Host header)
if settings.trusted_hosts:
    app.add_middleware(TrustedHostMiddleware, allowed_hosts=settings.trusted_hosts)

# CORS (из настроек; по умолчанию — только localhost)
cors_origins: Sequence[str] = settings.cors_origins or ["http://localhost", "http://localhost:3000"]
app.add_middleware(
    CORSMiddleware,
    allow_origins=list(cors_origins),
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "PATCH", "DELETE", "OPTIONS"],
    allow_headers=["*"],
)


# ── ГЛОБАЛЬНЫЕ ОБРАБОТЧИКИ ОШИБОК (без бизнес-логики) ─────────────────────────
@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request, exc):
    return JSONResponse(
        status_code=422,
        content=jsonable_encoder({
            "detail": exc.errors(),
            "body": exc.body,
        }),
    )


# Можно добавить общий обработчик HTTPException и unexpected Exception при желании:
# from fastapi import HTTPException
# @app.exception_handler(HTTPException)
# async def http_exception_handler(_: Request, exc: HTTPException) -> JSONResponse:
#     return JSONResponse(status_code=exc.status_code, content={"detail": exc.detail})


# ── РОУТЕРЫ ───────────────────────────────────────────────────────────────────
# Здесь только подключение. Сами обработчики — в .api.*
app.include_router(api_router)


# ── ПРИМЕЧАНИЕ ────────────────────────────────────────────────────────────────
# Из обработчиков ты сможешь получить exchange так:
#   exchange: aio_pika.abc.AbstractExchange = request.app.state.amqp_exchange
# и публиковать события:
#   await exchange.publish(aio_pika.Message(body=payload), routing_key="order_created")