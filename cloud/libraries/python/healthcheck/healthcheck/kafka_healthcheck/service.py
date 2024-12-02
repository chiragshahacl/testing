import asyncio
import random
from datetime import datetime, timedelta
from typing import Callable, Coroutine, TypeVar

from aiokafka.errors import KafkaError
from loguru import logger

from healthcheck.kafka_healthcheck.consumer import get_healthcheck_consumer
from healthcheck.kafka_healthcheck.producer import get_healthcheck_producer
from healthcheck.schemas import HealthcheckRecord
from healthcheck.settings import settings

Args = TypeVar("Args")
Kwargs = TypeVar("Kwargs")


class KafkaHealthcheckService:
    _instance = None

    #  Random backoff to avoid synchronized failures
    random_backoff_seconds = random.randint(1 * 60, 5 * 60)

    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            cls._instance = super(KafkaHealthcheckService, cls).__new__(
                cls, *args, **kwargs
            )
        return cls._instance

    def __init__(self):
        if not hasattr(self, "initialized"):
            self.health_record = HealthcheckRecord(timestamp=datetime.utcnow())
            self.producer = None
            self.consumer = None
            self.task = None
            self.stopped = True
            self.initialized = True

    async def ping(self):  # pragma: no cover
        while True:
            try:
                await self.producer.send_and_wait(topic="healthcheck", value=b"PING")
                await asyncio.sleep(settings.KAFKA_HEALTHCHECK_PERIOD_SECONDS)
            except KafkaError as exc:
                if exc.retriable:
                    # We can keep producing if the error is retriable
                    continue
                raise

    async def pong(self):  # pragma: no cover
        while True:
            try:
                async for _ in self.consumer:
                    self.health_record.timestamp = datetime.utcnow()
            except KafkaError as exc:
                if exc.retriable:
                    # We can keep consuming if the error is retriable
                    continue
                raise

    async def start(self):
        self.producer = await get_healthcheck_producer()
        self.consumer = await get_healthcheck_consumer()
        self.stopped = False

    async def run(self):
        assert (
            not self.stopped
        ), "KafkaHealthcheckService must be started before running"

        await asyncio.gather(self.pong(), self.ping())

    async def stop(self):
        if self.task and not self.task.done():
            self.task.cancel()

        if self.producer:
            await self.producer.stop()
            self.producer = None

        if self.consumer:
            await self.consumer.stop()
            self.consumer = None

        self.stopped = True

    async def flush(self):
        assert (
            not self.stopped
        ), "KafkaHealthcheckService must be started before flushing"

        await self.producer.flush()

    async def watchdog(
        self,
        func: Callable[[Args, Kwargs], Coroutine],
        *args: Args,
        **kwargs: Kwargs,
    ):  # pragma: no cover, pylint: disable=too-many-nested-blocks
        assert not self.stopped, "Healthcheck is not running, call start first"

        logger.debug("Starting Kafka healthcheck")

        self.task = asyncio.create_task(self.run())

        logger.debug(f"Starting {func.__name__} task")
        guarded_task = asyncio.create_task(func(*args, **kwargs))

        try:
            while True:
                await asyncio.sleep(settings.KAFKA_HEALTHCHECK_PERIOD_SECONDS)

                if not self.is_healthy():
                    logger.error("Kafka connection failed.")

                    if not guarded_task.done():
                        logger.error(f"Stopping {func.__name__}")
                        guarded_task.cancel()

                    # Wait for Kafka to respond
                    while not self.is_healthy():
                        await asyncio.sleep(settings.KAFKA_HEALTHCHECK_PERIOD_SECONDS)
                        try:
                            await asyncio.wait_for(
                                self.flush(),
                                timeout=settings.KAFKA_HEALTHCHECK_PERIOD_SECONDS,
                            )
                        except asyncio.TimeoutError:
                            logger.error("Retrying Kafka connection")

                    logger.info(
                        f"Kafka connection re-established: Restarting {func.__name__}"
                    )

                    # Restart guarded task
                    if guarded_task.done() or guarded_task.cancel():
                        guarded_task = asyncio.create_task(func(*args, **kwargs))
                    else:
                        logger.error(f"Failed to respawn: {func.__name__}")
        except asyncio.CancelledError:
            logger.info("Shutting down watchdog")
            guarded_task.cancel()
            await self.stop()

    def is_healthy(self) -> bool:
        current_time = datetime.utcnow()
        tolerance = timedelta(seconds=settings.KAFKA_HEALTHCHECK_TOLERANCE_SECONDS)
        return self.health_record.timestamp > current_time - tolerance

    def is_critical_failure(self) -> bool:
        current_time = datetime.utcnow()
        maximum_tolerance_minutes = timedelta(
            minutes=settings.KAFKA_HEALTHCHECK_MAXIMUM_TOLERANCE_MINUTES
        ) + timedelta(seconds=self.random_backoff_seconds)
        return self.health_record.timestamp <= current_time - maximum_tolerance_minutes
