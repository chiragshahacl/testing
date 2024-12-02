import abc
from typing import Generic, Optional, Tuple, Type, TypeAlias, TypeVar

from fastapi import Depends
from sqlalchemy import UUID
from sqlalchemy.ext.asyncio import AsyncSession

from app.common.database import get_db_session
from app.common.event_sourcing.events import Event
from app.common.event_sourcing.publisher import PublisherBackend
from app.common.models import Entity
from app.common.utils import load_backend
from app.settings import config

Publisher = load_backend(config.PUBLISHER_BACKEND)


T = TypeVar("T", bound=Entity)
Z = TypeVar("Z", bound=Entity)
UpdateData: TypeAlias = Tuple[Event[T], Optional[T]]


class BaseEventStream(abc.ABC, Generic[T]):
    _publisher: PublisherBackend

    def __init__(self, db_session: AsyncSession = Depends(get_db_session)):
        self._db_session = db_session
        self._publisher = Publisher()

    def _get_generic_type(self) -> Type:
        return self.__class__.__orig_bases__[0].__args__[0]  # pylint: disable=no-member

    async def notify(self, event: Event[T], related_entity_id: UUID) -> None:
        await self._publisher.notify(event, {}, {}, str(related_entity_id))

    async def add(
        self, event: Event, entity: Optional[T], related_entity_id: Optional[UUID] = None
    ) -> T:
        previous_state = {} if not entity else entity.as_dict()
        processed_entity = event.process(entity)
        new_state = processed_entity.as_dict()
        self._db_session.add(processed_entity)
        await self._db_session.flush()
        await self._publisher.notify(
            event,
            previous_state,
            new_state,
            str(related_entity_id) if related_entity_id else None,
        )
        return processed_entity
