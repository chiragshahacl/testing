import abc
import asyncio
from typing import Generic, List, Optional, Tuple, Type, TypeAlias, TypeVar

from fastapi import Depends
from sqlalchemy import UUID, delete, insert, update
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

    async def batch_add(self, events: List[UpdateData[T]]) -> List[T]:
        processed_events = []
        previous_states = []
        new_states = []
        processed_entities = []
        processed_entities_dicts = []
        is_create_event = events and events[0][1] is None  # It does not have an entity
        for event, entity in events:
            previous_states.append({} if not entity else entity.as_dict())
            processed_entity = event.process(entity)
            new_states.append(processed_entity.as_dict())
            processed_events.append(event)
            processed_entities.append(processed_entity)
            processed_entities_dicts.append(processed_entity.__dict__)
        if is_create_event:
            await self._db_session.execute(
                insert(self._get_generic_type()), processed_entities_dicts
            )
        else:
            await self._db_session.execute(
                update(self._get_generic_type()),
                processed_entities_dicts,
                execution_options={"synchronize_session": False},
            )
        await self._db_session.flush()
        await asyncio.gather(
            *[
                self._publisher.notify(processed_events[i], previous_states[i], new_states[i])
                for i in range(len(processed_entities))
            ]
        )
        return processed_entities

    async def delete(
        self, event: Event, entity: T, related_entity_id: Optional[UUID | str] = None
    ) -> T:
        previous_state = {} if not entity else entity.as_dict()
        deleted_entity = event.process(entity)
        new_state = deleted_entity.as_dict()
        await self._db_session.delete(deleted_entity)
        await self._db_session.flush()
        await self._publisher.notify(
            event,
            previous_state,
            new_state,
            str(related_entity_id) if related_entity_id else None,
        )
        return deleted_entity

    async def batch_delete(
        self, events: List[UpdateData[T]], related_entity_id: Optional[UUID | str] = None
    ) -> List[T]:
        processed_events = []
        previous_states = []
        new_states = []
        processed_entities = []
        processed_entities_dicts = []
        for event, entity in events:
            previous_states.append(entity.as_dict())
            processed_entity = event.process(entity)
            new_states.append(processed_entity.as_dict())
            processed_events.append(event)
            processed_entities.append(processed_entity)
            processed_entities_dicts.append(processed_entity.__dict__)

        stmt = delete(self._get_generic_type()).where(
            self._get_generic_type().id.in_([entity.id for entity in processed_entities])
        )
        await self._db_session.execute(
            stmt,
            execution_options={"synchronize_session": False},
        )

        await asyncio.gather(
            *[
                self._publisher.notify(
                    processed_events[i],
                    previous_states[i],
                    new_states[i],
                    str(related_entity_id) if related_entity_id else None,
                )
                for i in range(len(processed_entities))
            ]
        )
        return processed_entities
