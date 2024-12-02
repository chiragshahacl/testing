from aiokafka import AIOKafkaProducer
from loguru import logger

from healthcheck.kafka_healthcheck.ssl import get_ssl_context
from healthcheck.settings import settings


async def get_healthcheck_producer():
    url = f"{settings.KAFKA_HOST}:{settings.KAFKA_PORT}"
    logger.debug(f"Kafka healthcheck producing on address: {url}")

    if settings.ENVIRONMENT == "local":
        client = AIOKafkaProducer(bootstrap_servers=url)
    else:
        client = AIOKafkaProducer(
            bootstrap_servers=f"{settings.KAFKA_HOST}:{settings.KAFKA_PORT}",
            security_protocol="SSL",
            ssl_context=get_ssl_context(),
        )
    await client.start()
    return client
