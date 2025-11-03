# conftest.py
import os
import pytest
from httpx import AsyncClient, ASGITransport
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from sqlalchemy.pool import StaticPool
from unittest.mock import AsyncMock, patch
from contextlib import asynccontextmanager
import datetime

import sys
from pathlib import Path

# Add the project root to Python path
project_root = str(Path(__file__).parent.parent.parent)
if project_root not in sys.path:
    sys.path.insert(0, project_root)

from src.db.base import Base
from src.main import app
from src.api.dependencies import get_db, get_exchange
from src.db.models.orders import Order
from src.models.order_dto import OrderCreate
import aio_pika

# Provide a default mock exchange on app.state so sync TestClient can access it
app.state.amqp_exchange = AsyncMock(spec=aio_pika.Exchange)


# ==============================
# 🚫 ОТКЛЮЧАЕМ LIFESPAN/СТАРТОВЫЕ КОННЕКТЫ
# ==============================
# Вариант 1: полностью выключим lifespan у httpx-транспорта (см. fixture client)
# Вариант 2 (доп): перестраховка — заменим lifespan контекст на пустой

@asynccontextmanager
async def _no_lifespan(_app):
    # ничего не делаем на старте/остановке
    yield

# Если в app уже установлен другой lifespan, переопределим:
app.router.lifespan_context = _no_lifespan


# ==============================
# 🚀 SQLITE ENGINE (shared in-memory)
# ==============================
@pytest.fixture(scope="session")
async def test_engine():
    """Create a shared in-memory SQLite database engine for testing."""
    engine = create_async_engine(
        "sqlite+aiosqlite:///:memory:?cache=shared",
        echo=False,
        poolclass=StaticPool,
        connect_args={"uri": True},
    )
    from sqlalchemy import text

    try:
        async with engine.begin() as conn:
            await conn.execute(text("PRAGMA foreign_keys=ON"))
            await conn.run_sync(Base.metadata.create_all)
        
        yield engine
    
    finally:
        # Clean up database and dispose engine
        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.drop_all)
        await engine.dispose()

@pytest.fixture
async def db_session(test_engine):
    """Create a fresh database session for each test."""
    async_session = async_sessionmaker(test_engine, expire_on_commit=False)
    async with async_session() as session:
        yield session
        await session.rollback()

@pytest.fixture
async def sample_order(db_session):
    """Create a sample order for testing."""
    order = Order(
        user_id=1,
        amount=100.0,
        created_at=datetime.datetime.utcnow(),
        status="pending"
    )
    db_session.add(order)
    await db_session.commit()
    await db_session.refresh(order)
    return order

@pytest.fixture
def sample_order_create():
    """Create a sample OrderCreate DTO for testing."""
    return OrderCreate(user_id=1, amount=100.0)

@pytest.fixture
async def mock_exchange():
    """Mock RabbitMQ exchange for testing."""
    mock = AsyncMock(spec=aio_pika.Exchange)
    mock.publish = AsyncMock()
    return mock

@pytest.fixture
async def client(db_session, mock_exchange):
    """Test client with mocked dependencies."""
    # Override dependencies
    async def override_get_db():
        yield db_session

    async def override_get_exchange():
        return mock_exchange

    app.dependency_overrides[get_db] = override_get_db
    app.dependency_overrides[get_exchange] = override_get_exchange
    # Use ASGITransport so the client talks to the FastAPI app without network
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as test_client:
        try:
            yield test_client
        finally:
            # Clear dependency overrides after test
            app.dependency_overrides.clear()