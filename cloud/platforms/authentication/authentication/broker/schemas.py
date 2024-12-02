from datetime import datetime
from uuid import UUID

from pydantic import BaseModel

from authentication.constants import EVENT_ENTITY_NAME, EVENT_SYS_NAME, EVENT_TYPE


class EventSchema(BaseModel):
    entity_id: str
    event_name: str
    performed_on: datetime
    performed_by: str
    entity_name: str = EVENT_SYS_NAME
    emitted_by: str = EVENT_ENTITY_NAME
    event_type: str = EVENT_TYPE
    message_id: UUID
