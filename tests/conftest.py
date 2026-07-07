import pytest
from unittest.mock import AsyncMock, patch
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, AsyncEngine
from API_SCHEMAS import app, db_helper, broker, Base, encode_jwt, rabbit_settings
from checker import app as faststream_app, insert_in_db, ses_control_db, broker as c_broker, rabbit_settings as c_rabbit_settings, Base as c_Base
from sendler import broker as s_broker, rabbit_settings as s_rabbit_settings
from sqlalchemy.pool import StaticPool
from collections.abc import AsyncGenerator
from httpx import AsyncClient, ASGITransport, Cookies
from faststream.rabbit import TestRabbitBroker, RabbitBroker
from fast_depends import dependency_provider
from contextlib import asynccontextmanager
from testcontainers.rabbitmq import RabbitMqContainer
import asyncio

url_api = 'sqlite+aiosqlite:///file:API?mode=memory&cache=shared'
url_checker = 'sqlite+aiosqlite:///file:CHEKCER?mode=memory&cache=shared'

http_mock = patch('checker.check.check_from_sites')


@pytest.fixture(scope='function')
async def async_engine_api():
    engine = create_async_engine(url=url_api, poolclass=StaticPool)
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield engine
    await engine.dispose()


@pytest.fixture(scope='function')
async def async_engine_checker():
    engine = create_async_engine(url=url_checker, poolclass=StaticPool)
    async with engine.begin() as conn:
        await conn.run_sync(c_Base.metadata.drop_all)
        await conn.run_sync(c_Base.metadata.create_all)
    yield engine
    await engine.dispose()



@pytest.fixture
async def test_db_api(async_engine_api: AsyncEngine) -> AsyncGenerator[AsyncSession, None]:
    async with async_engine_api.connect() as conn:
        async with conn.begin() as trans:
            async_session = AsyncSession(bind=conn, expire_on_commit=False)

            app.dependency_overrides[db_helper] = lambda: async_session

            yield async_session

            app.dependency_overrides.clear()

            await trans.rollback()


@asynccontextmanager
async def same_ses(ses: AsyncSession):
    yield ses


@pytest.fixture
async def test_db_checker(async_engine_checker: AsyncEngine) -> AsyncGenerator[AsyncSession, None]:
    async with async_engine_checker.connect() as conn:
        async with conn.begin() as trans:
            async_session = AsyncSession(bind=conn, expire_on_commit=False)

            dependency_provider.override(ses_control_db, lambda: async_session)


            monkey_patch = pytest.MonkeyPatch()

            monkey_patch.setattr("checker.check.ses_control", lambda: same_ses(async_session))


            yield async_session


            dependency_provider.clear()


            await trans.rollback()


@pytest.fixture
async def request_to_test_server():
    original_request = broker.request

    broker.request = AsyncMock(return_value={"status": "success", "processed": True})

    async with AsyncClient(transport=ASGITransport(app=app), base_url='http://test') as c:
        yield c

    
    broker.request = original_request


@pytest.fixture
async def request_to_test_server_without_mock():
    async with AsyncClient(transport=ASGITransport(app=app), base_url='http://test') as c:
        yield c


@pytest.fixture
async def get_auth_token():
    token = encode_jwt(payload={'id': 1, 'sub': 'bogdanlavrenenko@gmail.com'})

    cookie = {'web-app-session-id': token}

    return cookie


@pytest.fixture
async def rabbit_container():
    rabbit = RabbitMqContainer()
    rabbit.with_bind_ports(5672, 5672)

    broker._connection_kwargs['url'] = rabbit_settings.rabbit_url_to_dev

    c_broker._connection_kwargs['url'] = c_rabbit_settings.rabbit_url_to_dev

    s_broker._connection_kwargs['url'] = s_rabbit_settings.rabbit_url_to_dev

    with rabbit:
        await broker.start()
        await c_broker.start()
        await s_broker.start()

        yield rabbit

        await broker.stop()
        await c_broker.stop()
        await s_broker.stop()











