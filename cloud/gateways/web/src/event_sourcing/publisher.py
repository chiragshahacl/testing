import datetime
import uuid
from abc import ABC, abstractmethod
from typing import Any, Dict

from aiokafka import AIOKafkaProducer
from loguru import logger

from src.event_sourcing import get_ssl_context
from src.event_sourcing.events import Event
from src.event_sourcing.schemas import EventSchema
from src.settings import settings


class KafkaProducerFactory:
    _instance = None

    def __new__(cls, *args, **kwargs):
        if not cls._instance:
            cls._instance = super(KafkaProducerFactory, cls).__new__(cls)
        return cls._instance

    def __init__(self):
        if not hasattr(self, "_initialized"):
            self.client = None
            self._initialized = True

    async def __call__(self, *args, **kwargs):
        if not self.client:
            url = f"{settings.KAFKA_HOST}:{settings.KAFKA_PORT}"
            logger.debug(f"Kafka Url: {url}")
            if settings.ENVIRONMENT == "local":
                self.client = AIOKafkaProducer(bootstrap_servers=url)
            else:
                self.client = AIOKafkaProducer(
                    bootstrap_servers=f"{settings.KAFKA_HOST}:{settings.KAFKA_PORT}",
                    security_protocol="SSL",
                    ssl_context=get_ssl_context(),
                )
            await self.client.start()
        return self.client


class PublisherBackend(ABC):
    @abstractmethod
    async def notify(
        self, event: Event, previous_state: Dict[str, Any], new_state: Dict[str, Any]
    ) -> None:
        """Publish event to stream"""

    @staticmethod
    def get_schema(
        event: Event, previous_state: Dict[str, Any], new_state: Dict[str, Any]
    ) -> EventSchema:
        return EventSchema.model_construct(
            entity_id=str(new_state["id"]),
            event_name=event.display_name,
            performed_by=event.username,
            performed_on=datetime.datetime.now(),
            event_state=new_state,
            previous_state=previous_state,
            event_type=event.event_type,
            message_id=uuid.uuid4(),
        )


class ConsolePublisher(PublisherBackend):
    async def notify(
        self, event: Event, previous_state: Dict[str, Any], new_state: Dict[str, Any]
    ) -> None:
        logger.info("========= Publishing Notification =========")
        logger.info(self.get_schema(event, previous_state, new_state))
        logger.info("========= Notification Published  =========")


class KafkaPublisher(PublisherBackend):
    async def notify(
        self, event: Event, previous_state: Dict[str, Any], new_state: Dict[str, Any]
    ) -> None:
        client = await KafkaProducerFactory()()
        schema = self.get_schema(event, previous_state, new_state)
        await client.send_and_wait(
            topic=settings.PUBLISHER_DEVICE_COMMAND_STREAM_NAME,
            value=str.encode(schema.model_dump_json()),
            headers=[("event_type", str.encode(schema.event_type))],
        )
