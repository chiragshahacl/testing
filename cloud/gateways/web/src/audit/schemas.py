from datetime import datetime
from typing import Any, Dict, List
from uuid import UUID

from src.common.platform.audit import schemas as platform_audit_schemas
from src.common.schemas import WebBaseSchema


class WebAuditEvent(WebBaseSchema):
    entity_id: UUID
    event_name: str
    timestamp: datetime
    data: Dict[str, Any]

    @classmethod
    def from_platform(cls, payload: platform_audit_schemas.PlatformAuditEvent) -> "WebAuditEvent":
        return cls.model_construct(
            entity_id=payload.entity_id,
            timestamp=payload.timestamp,
            data=payload.data,
            event_name=payload.event_name,
        )


class WebAuditResources(WebBaseSchema):
    resources: List[WebAuditEvent]

    @classmethod
    def from_platform(
        cls, payload: platform_audit_schemas.PlatformAuditResources
    ) -> "WebAuditResources":
        return cls.model_construct(
            resources=[WebAuditEvent.from_platform(event) for event in payload.resources],
        )
