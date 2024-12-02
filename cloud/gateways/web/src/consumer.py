import json

from aiokafka import AIOKafkaConsumer
from aiokafka.errors import KafkaError
from loguru import logger

from src.cache import monitor_keep_alive
from src.event_processing.topics.device import process_device_commands_responses
from src.event_sourcing import get_ssl_context
from src.event_sourcing.schemas import IncomingDeviceCommandResponseSchema
from src.settings import settings


class KafkaConsumerFactory:
    _instance = None

    def __new__(cls, *args, **kwargs):
        if not cls._instance:
            cls._instance = super(KafkaConsumerFactory, cls).__new__(cls)
        return cls._instance

    def __init__(self):
        if not hasattr(self, "_initialized"):
            self.consumer = None
            self._initialized = True

    async def __call__(self) -> AIOKafkaConsumer:
        url = f"{settings.KAFKA_HOST}:{settings.KAFKA_PORT}"
        if not self.consumer:
            if settings.ENVIRONMENT == "local":
                self.consumer = AIOKafkaConsumer(
                    settings.PM_STATE_TOPIC,
                    bootstrap_servers=url,
                    retry_backoff_ms=settings.KAFKA_RETRY_BACKOFF,
                    key_deserializer=self.deserializer,
                    value_deserializer=self.deserializer,
                    metadata_max_age_ms=settings.KAFKA_METADATA_MAX_AGE,
                )
            else:
                self.consumer = AIOKafkaConsumer(
                    settings.PM_STATE_TOPIC,
                    bootstrap_servers=url,
                    key_deserializer=self.deserializer,
                    value_deserializer=self.deserializer,
                    security_protocol="SSL",
                    ssl_context=get_ssl_context(),
                    retry_backoff_ms=settings.KAFKA_RETRY_BACKOFF,
                    metadata_max_age_ms=settings.KAFKA_METADATA_MAX_AGE,
                )
            await self.consumer.start()
        return self.consumer

    @staticmethod
    def deserializer(message):
        if message:
            return message.decode()
        return None


async def process_consumer_message(message_topic: str, message: dict) -> None:
    if message_topic == settings.PM_STATE_TOPIC:
        monitor_id = message["payload"]["device_primary_identifier"]
        monitor_keep_alive(monitor_id)
    elif message_topic == settings.DEVICE_COMMAND_RESPONSE_TOPIC:
        command_response = IncomingDeviceCommandResponseSchema(**message)
        await process_device_commands_responses(command_response)
    else:
        event_type = message.get("event_type")
        logger.info(f"Ignored device event {event_type}.")


async def event_consumer(consumer: AIOKafkaConsumer):
    keep_alive = True
    while keep_alive:
        try:
            async for msg in consumer:
                message_topic = msg.topic
                message = json.loads(msg.value)
                await process_consumer_message(message_topic, message)
        except KafkaError as kafka_error:
            logger.exception(kafka_error)
            if not kafka_error.retriable:
                keep_alive = False
        except Exception as exc:
            logger.exception(f"pm_state: {exc}")
