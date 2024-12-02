import importlib
import io
import urllib.parse
from datetime import datetime
from pathlib import Path
from unittest import mock
from uuid import UUID

from alembic import command
from alembic.config import Config as AlembicConfig
from behave import fixture, use_fixture
from behave.runner import Context
from sqlalchemy import Connection, create_engine, text
from sqlalchemy.engine import Engine
from sqlalchemy.orm import Session, sessionmaker
from starlette.testclient import TestClient

from app.common import database as database_module
from app.common.event_sourcing import publisher
from app.main import create_app

BASE_DIR = Path(__file__).parent.parent


class AnyDateTime:
    def __init__(self, allow_empty: bool = False):
        self.allow_empty = allow_empty

    def __eq__(self, other):
        if self.allow_empty and not other:
            return True
        try:
            if isinstance(other, AnyDateTime):
                return True
            if isinstance(other, datetime):
                return True
            datetime.fromisoformat(other)
        except Exception:
            return False
        return True

    def __repr__(self):
        return "<----:AnyDateTime:---->"


class AnyUUID:
    def __eq__(self, other):
        try:
            if isinstance(other, UUID):
                return True
            UUID(other)
        except Exception:
            return False
        return True

    def __repr__(self):
        return "<-------:AnyUUID:--------->"


def get_new_db_engine() -> Engine:
    engine = create_engine(
        database_module.get_db_sync_url(),
        pool_pre_ping=False,
        pool_reset_on_return="rollback",
    )
    return engine


def get_new_db_session(engine: Engine) -> Session:
    return Session(engine)


def database_exists(connection: Connection) -> bool:
    result = connection.execute(
        text("SELECT datname FROM pg_catalog.pg_database WHERE datname = 'test_auth'")
    )
    return bool(result.all())


def get_alembic_config() -> [AlembicConfig, io.StringIO]:
    output_buffer = io.StringIO()
    alembic_cfg = AlembicConfig(stdout=output_buffer)
    alembic_cfg.set_main_option("script_location", str(BASE_DIR / "migrations"))
    alembic_cfg.set_main_option("sqlalchemy.url", database_module.get_db_sync_url())
    return alembic_cfg, output_buffer


def run_migrations_up_to(up_to: str):
    mock.patch("migrations.env.settings.DATABASE_URL", database_module.get_db_sync_url())
    alembic_cfg, _ = get_alembic_config()
    command.upgrade(alembic_cfg, up_to)


@fixture
def create_test_client(context):
    app = create_app()
    context.client = TestClient(app, raise_server_exceptions=True)
    yield context.client


@fixture
def create_db_session(context: Context) -> Session:
    engine = get_new_db_engine()
    session_factory = sessionmaker(
        bind=engine, autocommit=False, autoflush=True, expire_on_commit=False
    )

    with session_factory() as session:
        context.db = session
        yield session


@fixture
def clean_database(_: Context) -> None:
    connection_info = urllib.parse.urlparse(database_module.get_db_sync_url())
    database_server_url = (
        f"postgresql+psycopg2://{connection_info.username}:{connection_info.password}@127.0.0.1"
    )
    engine = create_engine(database_server_url, isolation_level="AUTOCOMMIT")
    with engine.connect() as connection:
        if database_exists(connection):
            connection.execute(text("REVOKE CONNECT ON DATABASE test_auth FROM public;"))
            connection.execute(
                text(
                    """
                SELECT pid, pg_terminate_backend(pid)
                FROM pg_stat_activity
                WHERE datname = 'test_auth' AND pid <> pg_backend_pid();
                """
                )
            )
            connection.execute(text("DROP DATABASE IF EXISTS test_auth;"))
        connection.execute(text("CREATE DATABASE test_auth"))
        connection.execute(text("GRANT CONNECT ON DATABASE test_auth TO public;"))
    run_migrations_up_to("head")
    importlib.reload(database_module)


@fixture
def mock_producer(context):
    kafka_client_mock = mock.AsyncMock()
    kafka_client_mock.return_value = mock.AsyncMock()
    with mock.patch(
        "app.common.event_sourcing.publisher.KafkaProducerClient",
        kafka_client_mock,
    ):
        kafka_client_mock.return_value.start = mock.AsyncMock()
        kafka_client_mock.return_value.send_and_wait = mock.AsyncMock()
        kafka_client_mock.return_value.stop = mock.AsyncMock()
        context.producer = kafka_client_mock.return_value
        yield
    importlib.reload(publisher)


def before_scenario(context, _):
    use_fixture(clean_database, context)
    use_fixture(create_test_client, context)
    use_fixture(create_db_session, context)
    use_fixture(mock_producer, context)
