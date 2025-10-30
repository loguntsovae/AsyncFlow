from typing import AsyncGenerator
from src.db.base import async_session


async def get_db() -> AsyncGenerator:
    """Создает и закрывает асинхронную сессию SQLAlchemy."""
    async with async_session() as session:
        yield session
