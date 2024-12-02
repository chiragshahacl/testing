import importlib
from unittest import mock

import pytest
import pytest_asyncio
import respx
from aiokafka import AIOKafkaProducer
from fastapi.testclient import TestClient
from features.environment import clean_database
from sqlalchemy import create_engine
from sqlalchemy.engine import Engine
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.orm import Session

from app.common import database as database_module
from app.common.event_sourcing import publisher as publisher_module
from app.event_processing.subscriber import EventSubscriber
from app.main import app


@pytest.fixture
@respx.mock
def test_app():
    """Test app with mocked HTTPX requests"""
    return TestClient(app, raise_server_exceptions=False)


@pytest.fixture(scope="session", autouse=True)
def setup_db():
    clean_database(None)


@pytest.fixture(scope="function", autouse=True)
def producer_mock():
    producer_mock = mock.AsyncMock(spec=AIOKafkaProducer)
    with mock.patch(
        "app.common.event_sourcing.publisher.AIOKafkaProducer",
        return_value=producer_mock,
    ):
        yield producer_mock
    importlib.reload(publisher_module)


@pytest.fixture(scope="function", autouse=True)
def reset_subscriber():
    event_subscriber = EventSubscriber()
    event_subscriber.reset()
    yield
    delattr(event_subscriber, "_initialized")


@pytest_asyncio.fixture
async def async_db_session():
    engine = create_async_engine(
        url=database_module.get_db_async_url(),
        pool_pre_ping=False,
    )
    session_maker = async_sessionmaker(
        bind=engine,
        autocommit=False,
        autoflush=False,
        expire_on_commit=True,
        class_=AsyncSession,
    )
    async with session_maker() as db_session, db_session.begin():
        yield db_session
        await db_session.rollback()


def get_new_db_engine() -> Engine:
    engine = create_engine(
        database_module.get_db_sync_url(),
        pool_pre_ping=False,
        pool_reset_on_return="rollback",
    )
    return engine


def get_new_db_session(engine: Engine) -> Session:
    return Session(engine)
