from fastapi import Request
import aio_pika
from sqlalchemy.ext.asyncio import AsyncSession
from src.db.dependency import get_db


async def get_exchange(request: Request) -> aio_pika.abc.AbstractExchange:
    """Достаём общий exchange из FastAPI state."""
    return request.app.state.amqp_exchange