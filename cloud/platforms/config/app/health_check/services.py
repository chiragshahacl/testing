from fastapi import Depends
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from app.common.database import get_db_session
from app.health_check import schemas as health_schemas
from app.health_check.enums import HealthCheckStatus


class HealthCheckService:
    def __init__(self, db_session: AsyncSession = Depends(get_db_session)):
        self.db_session = db_session

    async def okay(self) -> health_schemas.HealthCheck:
        await self.db_session.execute(text("SELECT 1;"))
        response = health_schemas.HealthCheck(status=HealthCheckStatus.HEALTHY)
        return response
