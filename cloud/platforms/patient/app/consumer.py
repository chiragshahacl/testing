from aiokafka import AIOKafkaConsumer
from aiokafka.errors import (
    KafkaError,
)
from aiokafka.helpers import create_ssl_context
from loguru import logger

from app.event_processing.subscriber import BrokerMessage, EventSubscriber
from app.settings import config


class KafkaConsumerClientFactory:
    def __init__(self, *topics):
        self.client = None
        self.topics = (
            topics
            if topics
            else [
                config.EVENTS_ALERT_TOPIC,
                config.EVENTS_DEVICE_TOPIC,
                config.EVENTS_SDC_TOPIC,
                config.PATIENT_PUBLISHER_AUDIT_TRAIL_STREAM_NAME,
            ]
        )

    async def __call__(self, *args, **kwargs):
        if not self.client:
            url = f"{config.KAFKA_HOST}:{config.KAFKA_PORT}"
            logger.debug(f"Kafka Url: {url}")
            if config.ENVIRONMENT == "local":
                self.client = AIOKafkaConsumer(
                    *self.topics,
                    group_id=config.CONSUMER_PATIENT_GROUP_ID,
                    bootstrap_servers=url,
                    retry_backoff_ms=config.KAFKA_RETRY_BACKOFF,
                    metadata_max_age_ms=config.KAFKA_METADATA_MAX_AGE,
                )
            else:
                ssl_context = create_ssl_context(
                    cafile=config.KAFKA_CA_FILE_PATH,
                    certfile=config.KAFKA_CERT_FILE_PATH,
                    keyfile=config.KAFKA_KEY_FILE_PATH,
                    password=config.KAFKA_PASSWORD.get_secret_value(),
                )
                self.client = AIOKafkaConsumer(
                    *self.topics,
                    group_id=config.CONSUMER_PATIENT_GROUP_ID,
                    bootstrap_servers=f"{config.KAFKA_HOST}:{config.KAFKA_PORT}",
                    security_protocol="SSL",
                    ssl_context=ssl_context,
                    retry_backoff_ms=config.KAFKA_RETRY_BACKOFF,
                    metadata_max_age_ms=config.KAFKA_METADATA_MAX_AGE,
                )
            await self.client.start()
        return self.client


KafkaConsumerClient = KafkaConsumerClientFactory()


async def event_consumer(consumer: KafkaConsumerClient):
    event_subscriber = EventSubscriber()
    while True:
        try:
            async for msg in consumer:
                message = BrokerMessage.from_kafka_message(msg)
                await event_subscriber.notify(message)
        except KafkaError as kafka_error:
            logger.exception(kafka_error)
            if not kafka_error.retriable:
                break
        except Exception as error:
            logger.exception("Error parsing message", error)
    logger.info("Exiting broker consumer")
