import asyncio
import typing

from aiokafka import AIOKafkaConsumer
from aiokafka.errors import KafkaError
from aiokafka.helpers import create_ssl_context
from loguru import logger

from src.common.enums import HeaderEventTypes
from src.settings import config

DATA_TOPICS = {
    config.BROKER_TOPIC_VITALS,
    config.BROKER_TOPIC_ALERTS,
    config.BROKER_TOPIC_SDC_REALTIME_STATE,
    config.BROKER_TOPIC_SDC_EVENTS,
}
ALL_TOPICS = DATA_TOPICS.union(
    {
        config.BROKER_TOPIC_PATIENTS,
        config.BROKER_TOPIC_DEVICES,
    }
)


class KafkaClientFactory:
    consumer = None

    async def __call__(self) -> AIOKafkaConsumer:
        url = f"{config.KAFKA_HOST}:{config.KAFKA_PORT}"
        if not self.consumer:
            if config.ENVIRONMENT == "local":
                self.consumer = AIOKafkaConsumer(
                    *ALL_TOPICS,
                    bootstrap_servers=url,
                    retry_backoff_ms=config.KAFKA_RETRY_BACKOFF,
                    key_deserializer=self.deserializer,
                    value_deserializer=self.deserializer,
                    metadata_max_age_ms=config.KAFKA_METADATA_MAX_AGE,
                    auto_offset_reset="latest",
                )
            else:
                ssl_context = create_ssl_context(
                    cafile=config.KAFKA_CA_FILE_PATH,
                    certfile=config.KAFKA_CERT_FILE_PATH,
                    keyfile=config.KAFKA_KEY_FILE_PATH,
                    password=config.KAFKA_PASSWORD.get_secret_value(),
                )
                self.consumer = AIOKafkaConsumer(
                    *ALL_TOPICS,
                    bootstrap_servers=url,
                    key_deserializer=self.deserializer,
                    value_deserializer=self.deserializer,
                    security_protocol="SSL",
                    ssl_context=ssl_context,
                    retry_backoff_ms=config.KAFKA_RETRY_BACKOFF,
                    metadata_max_age_ms=config.KAFKA_METADATA_MAX_AGE,
                    auto_offset_reset="latest",
                )
            await self.consumer.start()
        return self.consumer

    @staticmethod
    def deserializer(message):
        if message:
            return message.decode()

    async def close(self):
        await self.consumer.stop()


KafkaClient = KafkaClientFactory()


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

    @property
    def is_vitals_message(self) -> bool:
        return (
            self.headers.event_type == HeaderEventTypes.NEW_METRICS.value
            or self.headers.event_type == HeaderEventTypes.NEW_WAVEFORM_VITALS.value
        )


AsyncEventHandler = typing.Callable[[BrokerMessage], typing.Awaitable[None]]


class EventSubscriber:
    _instance = None
    _key_handlers: dict[str, list[AsyncEventHandler]] = {}

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(EventSubscriber, cls).__new__(cls)
        return cls._instance

    def _register_handler(self, key: str, handler: AsyncEventHandler) -> None:
        handlers = self._key_handlers.get(key, [])
        handlers.append(handler)
        self._key_handlers[key] = handlers

    def register_event_type_handler(
        self,
        event_type: HeaderEventTypes,
        event_handler: AsyncEventHandler,
    ) -> None:
        self._register_handler(event_type, event_handler)

    def register_multi_event_type_handler(
        self,
        event_types: list[HeaderEventTypes],
        event_handler: AsyncEventHandler,
    ) -> None:
        for event_type in event_types:
            self._register_handler(event_type, event_handler)

    def register_topic_handler(
        self,
        topic: str,
        event_handler: AsyncEventHandler,
    ) -> None:
        self._register_handler(topic, event_handler)

    def register_multi_topic_handler(
        self, topics: list[str], event_handler: AsyncEventHandler
    ) -> None:
        for topic in topics:
            self._register_handler(topic, event_handler)

    async def notify(self, message: BrokerMessage) -> None:
        topic_handlers = self._key_handlers.get(message.source_topic, [])
        event_type_handlers = self._key_handlers.get(message.headers.event_type, [])
        all_handlers = topic_handlers + event_type_handlers
        await asyncio.gather(*[handler(message) for handler in all_handlers])

    def reset(self):
        self._key_handlers = {}


async def broker_consumer(consumer: KafkaClient):
    event_subscriber = EventSubscriber()
    loop = asyncio.get_running_loop()

    while True:
        try:
            async for msg in consumer:
                message = BrokerMessage.from_kafka_message(msg)
                loop.create_task(event_subscriber.notify(message))
        except KafkaError as kafka_error:
            logger.exception(kafka_error)
            if not kafka_error.retriable:
                break
        except Exception:
            logger.warning(f"Error parsing {msg.key} and headers {msg.headers}")

    await consumer.stop()
    logger.info("Exiting broker consumer")
