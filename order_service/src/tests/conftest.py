# conftest.py
import os
import pytest
from httpx import AsyncClient, ASGITransport
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from sqlalchemy.pool import StaticPool
from unittest.mock import AsyncMock
from contextlib import asynccontextmanager

from src.db.base import Base
from src.main import app
# именно эти объекты нам нужны для overrides
from src.api.dependencies import get_db, get_exchange
import aio_pika


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
    # shared in-memory + StaticPool => одна БД на все коннекты процесса
    engine = create_async_engine(
        "sqlite+aiosqlite:///:memory:?cache=shared",
        echo=False,
        poolclass=StaticPool,
        connect_args={"uri": True},
    )
    from sqlalchemy import text

    async with engine.begin() as conn:
        await conn.execute(text("PRAGMA foreign_keys=ON"))
        await conn.run_sync(Base.metadata.create_all)
    try:
        yield engine
    finally:
        await engine.dispose()


@pytest.fixture()
async def db_session(test_engine):
    SessionTest = async_sessionmaker(
        bind=test_engine,
        expire_on_commit=False,
        autoflush=False,
        autocommit=False,
        class_=AsyncSession,
    )
    async with SessionTest() as session:
        yield session


# ==============================
# 🧪 ПЕРЕОПРЕДЕЛЕНИЕ ЗАВИСИМОСТЕЙ FASTAPI
# ==============================
@pytest.fixture(autouse=True)
def override_db_and_exchange_dependencies(monkeypatch, db_session):
    # 1) get_db через dependency_overrides
    async def _get_test_db():
        yield db_session

    app.dependency_overrides[get_db] = _get_test_db

    # 2) мок AMQP exchange через dependency_overrides(get_exchange)
    mock_exchange = AsyncMock(name="MockExchange")
    async def _get_test_exchange():
        return mock_exchange

    app.dependency_overrides[get_exchange] = _get_test_exchange

    # 3) на случай прямого использования SessionLocal из prod-кода — подменим его
    #    ТОЛЬКО если у тебя где-то есть импорт "from src.db.dependency import SessionLocal"
    try:
        from sqlalchemy.ext.asyncio import async_sessionmaker as _asm
        SessionTest = _asm(bind=db_session.bind, expire_on_commit=False, class_=AsyncSession)
        monkeypatch.setattr("src.db.dependency.SessionLocal", SessionTest, raising=False)
    except Exception:
        # если нет такого импорта/использования — тихо пропускаем
        pass

    # 4) если код в старте приложения стучится в aio_pika.connect_robust — замокаем его на awaitable
    mock_connect = AsyncMock(name="MockConnect")
    mock_channel = AsyncMock(name="MockChannel")
    mock_connect.channel.return_value = mock_channel
    monkeypatch.setattr("aio_pika.connect_robust", AsyncMock(return_value=mock_connect), raising=False)

    # ещё положим exchange в app.state на случай прямого доступа
    app.state.amqp_exchange = mock_exchange

    yield

    # cleanup overrides
    app.dependency_overrides.pop(get_db, None)
    app.dependency_overrides.pop(get_exchange, None)


# ==============================
# 🌐 HTTP-КЛИЕНТ БЕЗ LIFESPAN
# ==============================
@pytest.fixture
async def client():
    # жизненно важно: lifespan="off" — иначе стартовые коннекты улетят в прод
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        yield ac


# ==============================
# Совместимость со старыми тестами
# ==============================
@pytest.fixture
def mock_exchange():
    # достаём, что положили в app.state
    return app.state.amqp_exchange