from datetime import datetime
from typing import Any, Dict, List

from src.common.schemas import BaseSchema


class PlatformAuditEvent(BaseSchema):
    entity_id: str
    event_name: str
    timestamp: datetime
    data: Dict[str, Any]


class PlatformAuditResources(BaseSchema):
    resources: List[PlatformAuditEvent]
    total: int
