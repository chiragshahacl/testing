import datetime
from typing import Any, Dict, List

from src.common.schemas import BaseSchema


class InternalAuditEventSchema(BaseSchema):
    entity_id: str
    event_name: str
    timestamp: datetime.datetime
    data: Dict[str, Any]


class InternalAuditEventResources(BaseSchema):
    resources: List[InternalAuditEventSchema]
    total: int


class IncomingMessageSchema(BaseSchema):
    entity_id: str
    event_name: str
    performed_on: datetime.datetime
    performed_by: str
    event_state: Dict[str, Any] = {}
    previous_state: Dict[str, Any] = {}
    entity_name: str
    emitted_by: str
    event_type: str
    message_id: str
    event_data: Dict[str, Any] = {}
