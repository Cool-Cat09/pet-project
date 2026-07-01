import pytest
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from API_SCHEMAS.database.engine import Base
from sqlalchemy.pool import StaticPool

url = 'sqlite+aiosqlite:///:memory:'

@pytest.fixture(scope='function')
async def async_engine():
    engine = create_async_engine(url=url, poolclass=StaticPool)
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield engine
    await engine.dispose()

@pytest.fixture
async def test_db(async_engine):
    async_session = sessionmaker(class_=AsyncSession, expire_on_commit=False, bind=async_engine)
    async with async_session() as session:
        yield session
        await session.rollback()

