import abc
import typing
from typing import Optional, TypeVar

from src.common.utils import load_backend
from src.device.schemas import DeviceCommandSchema
from src.event_sourcing.events import Event
from src.event_sourcing.publisher import PublisherBackend
from src.settings import settings

Publisher = load_backend(settings.PUBLISHER_BACKEND)


T = TypeVar("T")


class BaseEventStream(abc.ABC, typing.Generic[T]):
    _publisher: PublisherBackend

    def __init__(self):
        self._publisher = Publisher()

    async def add(self, event: Event, entity: Optional[T]) -> T:
        previous_state = {}
        processed_entity = event.process(entity)
        new_state = processed_entity.as_dict()
        await self._publisher.notify(event, previous_state, new_state)
        return processed_entity


class CommandExecutionEventStream(BaseEventStream[DeviceCommandSchema]):
    pass
