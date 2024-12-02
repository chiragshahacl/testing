import uuid
from abc import ABC, abstractmethod
from datetime import datetime

from authentication.broker.schemas import EventSchema


class PublisherBackend(ABC):
    @abstractmethod
    def notify(
        self,
        entity_id: str,
        event_name: str,
        performed_by: str,
    ) -> None:
        """Publish event to stream"""

    @staticmethod
    def get_schema(
        entity_id: str,
        event_name: str,
        performed_by: str,
    ) -> EventSchema:
        return EventSchema.model_construct(
            entity_id=entity_id,
            event_name=event_name,
            performed_by=performed_by,
            performed_on=datetime.now(),
            message_id=uuid.uuid4(),
        )
