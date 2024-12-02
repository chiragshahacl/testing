import asyncio
import typing
from enum import Enum

from loguru import logger


class HeaderEventTypes(str, Enum):
    DEVICE_DISCOVERED_EVENT = "DEVICE_DISCOVERED"
    ALERT_OBSERVATION_EVENT = "NEW_ALERT_OBSERVATION"
    DEVICE_CREATED_EVENT = "DEVICE_CREATED_EVENT"
    DEVICE_UPDATED_EVENT = "DEVICE_UPDATED_EVENT"
    DEVICE_SUBJECT_REMOVED = "DEVICE_SUBJECT_REMOVED"
    SENSOR_REMOVED_EVENT = "SENSOR_REMOVED_EVENT"
    ASSIGN_DEVICE_LOCATION_EVENT = "ASSIGN_DEVICE_LOCATION_EVENT"
    PATIENT_SESSION_CLOSED_EVENT = "PATIENT_SESSION_CLOSED_EVENT"
    DEVICE_NEW_VITALS_RANGES = "DEVICE_NEW_VITALS_RANGES"
    PM_CONFIGURATION_UPDATED = "PM_CONFIGURATION_UPDATED"
    PATIENT_SESSION_STARTED = "PATIENT_SESSION_STARTED"
    PATIENT_ADMISSION_REJECTED = "PATIENT_ADMISSION_REJECTED"


class BrokerMessageHeaders(typing.NamedTuple):
    event_type: str
    code: str | None = None
    device_primary_identifier: str | None = None
    patient_primary_identifier: str | None = None
    is_backfill: bool = False


class BrokerMessage(typing.NamedTuple):
    key: str | None
    source_topic: str
    value: str
    headers: BrokerMessageHeaders

    def __repr__(self) -> str:
        return f"<Message: key={self.key}, type={self.headers.event_type}"

    @classmethod
    def from_kafka_message(cls, kafka_message) -> "BrokerMessage":
        headers = {k: v.decode() for k, v in kafka_message.headers}
        return cls(
            key=kafka_message.key,
            value=kafka_message.value,
            source_topic=kafka_message.topic,
            headers=BrokerMessageHeaders(
                event_type=headers["event_type"],
                code=headers.get("code"),
                device_primary_identifier=headers.get("device_primary_identifier"),
                patient_primary_identifier=headers.get("patient_primary_identifier"),
            ),
        )


AsyncCallableType = typing.Callable[[BrokerMessage], typing.Awaitable[None]]


class EventSubscriber:
    _instance = None
    _key_handlers: dict[str, list[AsyncCallableType]] = {}

    def __init__(self):
        if not hasattr(self, "_initialized"):
            self._initialized = True

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(EventSubscriber, cls).__new__(cls)
            cls._instance._initialized = True
        return cls._instance

    def _register_handler(self, key: str, handler: AsyncCallableType) -> None:
        handlers = self._key_handlers.get(key, [])
        handlers.append(handler)
        self._key_handlers[key] = handlers

    def register_event_type_handler(
        self,
        event_type: HeaderEventTypes,
        event_handler: AsyncCallableType,
    ) -> None:
        self._register_handler(event_type, event_handler)

    def register_topic_handler(
        self,
        topic: str,
        event_handler: AsyncCallableType,
    ) -> None:
        self._register_handler(topic, event_handler)

    async def notify(self, message: BrokerMessage) -> None:
        logger.debug(f"New broker message: {message.headers.event_type}")
        topic_handlers = self._key_handlers.get(message.source_topic, [])
        event_type_handlers = self._key_handlers.get(message.headers.event_type, [])
        all_handlers = topic_handlers + event_type_handlers
        await asyncio.gather(*[handler(message) for handler in all_handlers])

    def reset(self):
        self._key_handlers = {}
