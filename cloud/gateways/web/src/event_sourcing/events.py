from abc import ABC, abstractmethod
from typing import Optional, TypeVar
from uuid import uuid4

from src.device.schemas import DeviceCommandSchema

T = TypeVar("T")


class Event(ABC):
    def __init__(self, username: str):
        self.username = username

    @property
    @abstractmethod
    def display_name(self) -> str:
        """Display name for the event"""

    @property
    @abstractmethod
    def event_type(self) -> str:
        """Event type for the event"""

    @abstractmethod
    def process(self, entity: Optional[T]) -> T:
        """Process command execution request event"""


class CommandExecutionRequestEvent(Event):
    display_name: str = "Command execution request"
    event_type: str = "COMMAND_EXECUTION_REQUEST"

    def __init__(self, username: str, payload: DeviceCommandSchema):
        super().__init__(username)
        self.payload = payload

    def process(self, entity: DeviceCommandSchema) -> DeviceCommandSchema:
        entity.request_id = uuid4()
        entity.command_name = self.payload.command_name
        entity.pm_id = self.payload.pm_id
        entity.params = self.payload.params
        return entity
