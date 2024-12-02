import json

from aiokafka import AIOKafkaConsumer
from aiokafka.errors import KafkaError
from aiokafka.helpers import create_ssl_context
from loguru import logger

from src.audit.schemas import IncomingMessageSchema
from src.common.database import session_maker
from src.common.models import InternalAudit
from src.settings import settings


class KafkaClientFactory:
    def __init__(self):
        self.client = None

    async def __call__(self, *args, **kwargs):
        if not self.client:
            url = f"{settings.KAFKA_HOST}:{settings.KAFKA_PORT}"
            logger.debug(f"Kafka Url: {url}")
            group_id = settings.CONSUMER_AUDIT_TRAIL_GROUP_ID
            if settings.ENVIRONMENT == "local":
                self.client = AIOKafkaConsumer(
                    settings.PATIENT_EVENTS_TOPIC,
                    settings.AUTH_EVENTS_TOPIC,
                    settings.DEVICE_EVENTS_TOPIC,
                    bootstrap_servers=url,
                    group_id=group_id,
                    retry_backoff_ms=settings.KAFKA_RETRY_BACKOFF,
                    metadata_max_age_ms=settings.KAFKA_METADATA_MAX_AGE,
                )
            else:
                ssl_context = create_ssl_context(
                    cafile=settings.KAFKA_CA_FILE_PATH,
                    certfile=settings.KAFKA_CERT_FILE_PATH,
                    keyfile=settings.KAFKA_KEY_FILE_PATH,
                    password=settings.KAFKA_PASSWORD,
                )
                self.client = AIOKafkaConsumer(
                    settings.PATIENT_EVENTS_TOPIC,
                    settings.AUTH_EVENTS_TOPIC,
                    settings.DEVICE_EVENTS_TOPIC,
                    bootstrap_servers=f"{settings.KAFKA_HOST}:{settings.KAFKA_PORT}",
                    security_protocol="SSL",
                    ssl_context=ssl_context,
                    group_id=group_id,
                    retry_backoff_ms=settings.KAFKA_RETRY_BACKOFF,
                    metadata_max_age_ms=settings.KAFKA_METADATA_MAX_AGE,
                )
            await self.client.start()
        return self.client


KafkaClient = KafkaClientFactory()


async def insert_audit_trail_event(message: IncomingMessageSchema) -> None:
    async with session_maker() as db_session, db_session.begin():
        processed_message = InternalAudit(
            message_id=message.message_id,
            entity_id=message.entity_id,
            timestamp=message.performed_on,
            event_name=message.event_name,
            data={
                "current_state": message.event_state,
                "previous_state": message.previous_state,
            },
            emitted_by=message.emitted_by,
            performed_by=message.performed_by,
            event_data=message.event_data,
        )
        db_session.add(processed_message)
        await db_session.commit()


# pylint: disable=W0718
async def internal_audit_trail_consumer() -> None:
    consumer = await KafkaClient()

    logger.info("Exiting broker consumer")
    keep_alive = True
    while keep_alive:
        async for msg in consumer:
            try:
                if msg.value:
                    message = IncomingMessageSchema(**json.loads(msg.value))
                    await insert_audit_trail_event(message)
            except KafkaError as kafka_error:
                logger.exception(kafka_error)
                if not kafka_error.retriable:
                    keep_alive = False
            except Exception as exc:
                logger.exception("Error processing message", exc)
    logger.warning("Closing consumer")
