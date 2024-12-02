import typing

from sqlalchemy.ext.asyncio import AsyncSession

from app.common.database import session_maker
from app.event_processing.subscriber import BrokerMessage

AsyncEventHandler = typing.Callable[[AsyncSession, BrokerMessage], typing.Awaitable[None]]


class DatabaseAdapter:
    def __init__(self, f: AsyncEventHandler):
        self.f = f

    async def __call__(self, message: BrokerMessage) -> None:
        async with session_maker() as db_session, db_session.begin():
            await self.f(db_session, message)
            await db_session.commit()
