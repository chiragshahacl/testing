import uuid
from abc import ABC, abstractmethod
from datetime import datetime
from typing import Any, Dict, Optional

from aiokafka import AIOKafkaProducer
from aiokafka.helpers import create_ssl_context
from loguru import logger

from app.common.event_sourcing.events import Event
from app.common.event_sourcing.schemas import EventSchema
from app.common.schemas import json_encode
from app.settings import config

# pylint: disable=duplicate-code


class KafkaProducerClientFactory:
    def __init__(self):
        self.client = None

    async def __call__(self, *args, **kwargs):
        if not self.client:
            url = f"{config.KAFKA_HOST}:{config.KAFKA_PORT}"
            logger.debug(f"Kafka Url: {url}")
            if config.ENVIRONMENT == "local":
                self.client = AIOKafkaProducer(bootstrap_servers=url)
            else:
                ssl_context = create_ssl_context(
                    cafile=config.KAFKA_CA_FILE_PATH,
                    certfile=config.KAFKA_CERT_FILE_PATH,
                    keyfile=config.KAFKA_KEY_FILE_PATH,
                    password=config.KAFKA_PASSWORD.get_secret_value(),
                )
                self.client = AIOKafkaProducer(
                    bootstrap_servers=f"{config.KAFKA_HOST}:{config.KAFKA_PORT}",
                    security_protocol="SSL",
                    ssl_context=ssl_context,
                )
            await self.client.start()
        return self.client


KafkaProducerClient = KafkaProducerClientFactory()


class PublisherBackend(ABC):
    @abstractmethod
    async def notify(
        self,
        event: Event,
        previous_state: Dict[str, Any],
        new_state: Dict[str, Any],
        related_entity_id: Optional[str] = None,
    ) -> None:
        """Publish event to stream"""

    @staticmethod
    def get_schema(
        event: Event,
        previous_state: Dict[str, Any],
        new_state: Dict[str, Any],
        related_entity_id: Optional[str] = None,
    ) -> EventSchema:
        actual_entity_id = related_entity_id if related_entity_id else str(new_state["id"])
        return EventSchema.model_construct(
            entity_id=actual_entity_id,
            event_name=event.display_name,
            performed_by=event.username,
            performed_on=datetime.now(),
            event_state=new_state,
            previous_state=previous_state,
            event_type=event.event_type,
            message_id=str(uuid.uuid4()),
            event_data=event.as_dict(),
        )


class ConsolePublisher(PublisherBackend):
    async def notify(
        self,
        event: Event,
        previous_state: Dict[str, Any],
        new_state: Dict[str, Any],
        related_entity_id: Optional[str] = None,
    ) -> None:
        schema = self.get_schema(event, previous_state, new_state, related_entity_id)
        logger.debug(schema.model_dump_json())


class KafkaPublisher(PublisherBackend):
    async def notify(
        self,
        event: Event,
        previous_state: Dict[str, Any],
        new_state: Dict[str, Any],
        related_entity_id: Optional[str] = None,
    ) -> None:
        client = await KafkaProducerClient()
        schema = self.get_schema(event, previous_state, new_state, related_entity_id)

        await client.send_and_wait(
            topic=config.PATIENT_PUBLISHER_AUDIT_TRAIL_STREAM_NAME,
            value=str.encode(json_encode(schema)),
            headers=[("event_type", str.encode(schema.event_type))],
        )
