import importlib
import io
import urllib.parse
from datetime import datetime
from pathlib import Path
from typing import Union
from unittest import mock

from alembic import command
from alembic.config import Config as AlembicConfig
from behave import fixture, use_fixture
from behave.runner import Context
from freezegun import freeze_time
from sqlalchemy import create_engine, text
from sqlalchemy.engine import Engine
from sqlalchemy.orm import Session, sessionmaker
from starlette.testclient import TestClient

from src.common import database as database_module
from src.main import create_app

BASE_DIR = Path(__file__).parent.parent


def get_new_db_engine() -> Engine:
    engine = create_engine(
        database_module.get_db_sync_url(),
        pool_pre_ping=False,
    )
    return engine


def get_new_db_session(engine: Engine) -> Session:
    return Session(engine)


def database_exists(engine: Engine) -> bool:
    with engine.connect() as conn:
        result = conn.execute(
            text("SELECT datname FROM pg_catalog.pg_database WHERE datname = 'test_audit_trail'")
        )
        return bool(result.all())


def get_alembic_config() -> Union[AlembicConfig, io.StringIO]:
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
    test_client = TestClient(app, raise_server_exceptions=True)
    context.client = test_client
    yield context.client
    test_client.close()


@fixture
def create_db_session(context: Context) -> Session:
    engine = create_engine(
        database_module.get_db_sync_url(),
        pool_pre_ping=False,
    )
    session_factory = sessionmaker(
        bind=engine, autocommit=False, autoflush=False, expire_on_commit=False
    )
    with session_factory() as session:
        context.db = session
        yield session


def clean_database(_: Context) -> None:
    connection_info = urllib.parse.urlparse(database_module.get_db_sync_url())
    database_server_url = (
        f"postgresql+psycopg2://{connection_info.username}:{connection_info.password}@127.0.0.1"
    )
    engine = create_engine(database_server_url, isolation_level="AUTOCOMMIT")
    with engine.connect() as conn:
        if database_exists(engine):
            conn.execute(text("REVOKE CONNECT ON DATABASE test_audit_trail FROM public;"))
            conn.execute(
                text(
                    "SELECT pid, pg_terminate_backend(pid) FROM pg_stat_activity WHERE datname = 'test_audit_trail' AND pid <> pg_backend_pid();"
                )
            )
            conn.execute(text("DROP DATABASE IF EXISTS test_audit_trail;"))
        conn.execute(text("CREATE DATABASE test_audit_trail"))
        conn.execute(text("GRANT CONNECT ON DATABASE test_audit_trail TO public;"))
    run_migrations_up_to("head")
    importlib.reload(database_module)


@fixture
def mock_dt(context):
    context.now = datetime(2023, 2, 8)
    with freeze_time(context.now):
        yield context.now


def before_all(context):
    use_fixture(mock_dt, context)


def before_scenario(context, _):
    use_fixture(clean_database, context)
    use_fixture(create_test_client, context)
    use_fixture(create_db_session, context)
