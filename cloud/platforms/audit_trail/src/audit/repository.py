from typing import List

from fastapi import Depends
from sqlalchemy import desc, select
from sqlalchemy.ext.asyncio import AsyncSession

from src.common.database import get_db_session
from src.common.models import InternalAudit


class AuditEventRepository:
    def __init__(self, db_session: AsyncSession = Depends(get_db_session)):
        self.db_session = db_session
        self.base_query = select(InternalAudit)

    async def get_audit_events_by_id(self, entity_id: str) -> List[InternalAudit]:
        result = await self.db_session.execute(
            self.base_query.where(InternalAudit.entity_id == entity_id).order_by(
                desc(InternalAudit.timestamp)
            )
        )
        return result.scalars().all()
