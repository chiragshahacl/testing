from datetime import datetime
from uuid import UUID

from app.common.schemas import BaseSchema
from app.event_processing.topics.events_sdc.schemas import SDCAlertPayload


class SDCNewAlertEvent(BaseSchema):
    message_id: UUID
    event_name: str
    event_type: str
    timestamp: datetime
    payload: SDCAlertPayload
