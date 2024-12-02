from datetime import datetime
from typing import Any, Dict, List, Optional
from uuid import UUID

from pydantic import BaseModel


class EventSchema(BaseModel):
    entity_id: str
    event_name: str
    performed_on: datetime
    performed_by: str
    event_state: Dict[str, Any]
    previous_state: Dict[str, Any] = {}
    entity_name: str
    emitted_by: str = "web"
    event_type: str
    message_id: UUID


class CommandResponseEventState(BaseModel):
    request_id: UUID
    success: bool
    errors: Optional[List[str]]


class IncomingDeviceCommandResponseSchema(EventSchema):
    event_state: CommandResponseEventState
