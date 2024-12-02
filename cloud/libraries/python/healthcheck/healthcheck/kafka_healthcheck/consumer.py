from uuid import uuid4

from aiokafka import AIOKafkaConsumer
from loguru import logger

from healthcheck.kafka_healthcheck.ssl import get_ssl_context
from healthcheck.settings import settings


async def get_healthcheck_consumer():
    url = f"{settings.KAFKA_HOST}:{settings.KAFKA_PORT}"
    logger.debug(
        f"Kafka healthcheck listening on address: {url}, "
        f"topic: {settings.KAFKA_HEALTHCHECK_TOPIC}"
    )

    config = {
        "bootstrap_servers": url,
        "retry_backoff_ms": settings.KAFKA_RETRY_BACKOFF,
        "metadata_max_age_ms": settings.KAFKA_METADATA_MAX_AGE,
        "auto_offset_reset": "latest",
        "group_id": str(uuid4()),
    }

    if settings.ENVIRONMENT == "local":
        client = AIOKafkaConsumer(settings.KAFKA_HEALTHCHECK_TOPIC, **config)
    else:
        client = AIOKafkaConsumer(
            settings.KAFKA_HEALTHCHECK_TOPIC,
            security_protocol="SSL",
            ssl_context=get_ssl_context(),
            **config,
        )
    await client.start()

    return client
