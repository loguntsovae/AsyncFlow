import pytest
from httpx import AsyncClient
from unittest.mock import AsyncMock

from src.main import app


@pytest.fixture
async def client():
    """Создаёт HTTP-клиент для FastAPI (без реального сервера)."""
    async with AsyncClient(app=app, base_url="http://test") as ac:
        yield ac


@pytest.fixture
def mock_exchange(monkeypatch):
    """Мокаем RabbitMQ exchange, чтобы не слать реальные сообщения."""
    mock = AsyncMock()
    monkeypatch.setattr("src.api.orders.get_exchange", lambda _: mock)
    return mock