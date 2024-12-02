import json

from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from app.settings import config


def get_db_url_no_driver() -> str:
    db_username = config.DB_USERNAME.get_secret_value()
    db_pass = config.DB_PASSWORD.get_secret_value()
    db_host = config.DB_HOST
    db_port = config.DB_PORT
    db_name = config.DB_NAME
    db_connection = f"{db_username}:{db_pass}@{db_host}:{db_port}/{db_name}"
    return db_connection


def get_db_sync_url() -> str:
    driver = "postgresql+psycopg2"
    db_connection = get_db_url_no_driver()
    return f"{driver}://{db_connection}"


def get_db_async_url() -> str:
    driver = "postgresql+asyncpg"
    db_connection = get_db_url_no_driver()
    return f"{driver}://{db_connection}"


def custom_serializer(obj):
    """
    Custom serializer to avoid re-serializing bytes.
    """
    if isinstance(obj, bytes):
        return obj.decode()
    return json.dumps(obj)


engine = create_async_engine(
    url=get_db_async_url(),
    pool_pre_ping=False,
    echo=False,
    json_serializer=custom_serializer,
)

session_maker = async_sessionmaker(
    bind=engine,
    autocommit=False,
    autoflush=False,
    expire_on_commit=False,
    class_=AsyncSession,
)


async def get_db_session():
    async with session_maker() as db_session, db_session.begin():
        yield db_session
        await db_session.commit()
