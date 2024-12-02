from abc import ABC, abstractmethod
from typing import Any, Generic, Optional, TypeVar

from app.common.models import Entity

T = TypeVar("T", bound=Entity)


class Event(ABC, Generic[T]):
    username: str

    def __init__(self, username: str):
        self.username = username

    @property
    @abstractmethod
    def event_type(self) -> str:
        """Type of the event"""

    @property
    @abstractmethod
    def display_name(self) -> str:
        """Display name for the event"""

    @abstractmethod
    def process(self, entity: Optional[T]) -> T:
        """Process entity event"""

    def as_dict(self) -> dict[Any, Any]:
        return {}
