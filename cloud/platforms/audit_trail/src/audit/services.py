from typing import Optional

from fastapi import Depends

from src.audit import schemas as audit_trail_schemas
from src.audit.repository import AuditEventRepository


class AuditTrailService:
    def __init__(self, audit_repository: AuditEventRepository = Depends()):
        self.audit_repository = audit_repository

    async def get_audit_trail(
        self, entity_id: str
    ) -> Optional[audit_trail_schemas.InternalAuditEventResources]:
        response_items = await self.audit_repository.get_audit_events_by_id(entity_id)
        count = len(response_items)

        if count == 0:
            return None

        return audit_trail_schemas.InternalAuditEventResources.construct(
            resources=[
                audit_trail_schemas.InternalAuditEventSchema.from_orm(i) for i in response_items
            ],
            total=count,
        )
