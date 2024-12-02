from fastapi import Depends
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.common.database import get_db_session
from app.config.models import SystemSettings


class ReadSystemSettingsRepository:
    def __init__(self, db_session: AsyncSession = Depends(get_db_session)):
        self.db_session = db_session

    async def get(self) -> SystemSettings:
        stmt = select(SystemSettings)
        result = await self.db_session.execute(stmt)
        return result.scalars().one()
