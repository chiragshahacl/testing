from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker

from src.settings import settings


def get_db_url_no_driver() -> str:
    db_username = settings.DB_USERNAME
    db_pass = settings.DB_PASSWORD
    db_host = settings.DB_HOST
    db_port = settings.DB_PORT
    db_name = settings.DB_NAME
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


engine = create_async_engine(
    url=get_db_async_url(),
    pool_pre_ping=False,
)

session_maker = sessionmaker(
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
