from datetime import datetime
from typing import Any, Dict
from uuid import UUID

from app.common.schemas import BaseSchema


class EventSchema(BaseSchema):
    entity_id: str
    event_name: str
    performed_on: datetime
    performed_by: str
    event_state: Dict[str, Any]
    previous_state: Dict[str, Any] = {}
    entity_name: str = "patient"
    emitted_by: str = "patient"
    event_type: str
    message_id: UUID
    event_data: Dict[str, Any] | None = None
