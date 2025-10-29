from fastapi import Request
from sqlalchemy.ext.asyncio import AsyncSession
import aio_pika

from src.db.dependency import get_db as _get_db

async def get_db() -> AsyncSession:
    """Переиспользуем зависимость для БД."""
    return await _get_db().__anext__()  # если хочешь унифицировать

async def get_exchange(request: Request) -> aio_pika.abc.AbstractExchange:
    """Достаём общий exchange из FastAPI state."""
    return request.app.state.amqp_exchange
