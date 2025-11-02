from sqlalchemy.ext.asyncio import AsyncEngine, AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker
from settings import settings

DATABASE_URL = settings.database_url

# Create an async engine
async_engine: AsyncEngine = create_async_engine(
    DATABASE_URL,
    echo=True,  # Enable SQL query logging
)

# Create an async sessionmaker
async_session = sessionmaker(
    bind=async_engine,
    class_=AsyncSession,
    expire_on_commit=False
)


# Dependency to get the async database session
async def get_db():
    async with async_session() as session:
        yield session


# Dependency to get the async engine
async def get_async_engine():
    return async_engine