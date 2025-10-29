import pytest
from httpx import AsyncClient, ASGITransport
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker
from sqlalchemy.pool import NullPool
from unittest.mock import AsyncMock
from src.db.base import Base
from src.main import app


# ==============================
# 🚀 DATABASE FIXTURES (SQLite)
# ==============================

@pytest.fixture(scope="session")
async def test_engine():
    """Создаёт in-memory SQLite движок один раз за сессию."""
    engine = create_async_engine(
        "sqlite+aiosqlite:///:memory:",
        echo=False,
        poolclass=NullPool,
    )
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield engine
    await engine.dispose()


@pytest.fixture()
async def db_session(test_engine):
    """Создаёт новую async-сессию на тестовой базе."""
    async_session = async_sessionmaker(
        bind=test_engine,
        expire_on_commit=False,
        autoflush=False,
        autocommit=False,
    )
    async with async_session() as session:
        yield session


@pytest.fixture(autouse=True)
def override_db_dependency(monkeypatch, db_session):
    """Переопределяет все get_db на SQLite-сессию."""
    async def _get_test_db():
        print("⚙️  Using TEST DB (SQLite)")
        yield db_session

    # Подменяем во всех возможных местах
    monkeypatch.setattr("src.db.dependency.get_db", _get_test_db)
    monkeypatch.setattr("src.api.dependencies.get_db", _get_test_db)
    monkeypatch.setattr("src.api.orders.get_db", _get_test_db)


# ==============================
# 🐇 RABBITMQ MOCK FIXTURES
# ==============================

@pytest.fixture(autouse=True)
def mock_rabbit_connection(monkeypatch):
    """Подменяет aio_pika.connect_robust, чтобы не коннектиться к реальному Rabbit."""
    mock_connect = AsyncMock(name="MockConnect")
    mock_channel = AsyncMock(name="MockChannel")
    mock_exchange = AsyncMock(name="MockExchange")

    mock_connect.channel.return_value = mock_channel
    mock_channel.declare_exchange.return_value = mock_exchange

    monkeypatch.setattr("aio_pika.connect_robust", lambda *_, **__: mock_connect)
    return mock_exchange


@pytest.fixture(autouse=True)
def mock_app_exchange(mock_rabbit_connection):
    """Добавляет мокнутый exchange в app.state."""
    app.state.amqp_exchange = mock_rabbit_connection
    return app.state.amqp_exchange


# ==============================
# 🌐 FASTAPI CLIENT FIXTURE
# ==============================

@pytest.fixture
async def client():
    """Создаёт HTTP-клиент с моками и тестовой БД."""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        yield ac

@pytest.fixture
def mock_exchange(mock_rabbit_connection):
    """Совместимая фикстура для старых тестов."""
    return mock_rabbit_connection
