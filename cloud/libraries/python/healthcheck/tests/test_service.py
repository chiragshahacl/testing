from datetime import datetime, timedelta
from unittest.mock import AsyncMock

import pytest
from freezegun import freeze_time
from healthcheck import KafkaHealthcheckService
from healthcheck.settings import settings


@pytest.fixture(autouse=True)
def reset_singleton():
    yield
    del KafkaHealthcheckService().initialized


@pytest.mark.asyncio
async def test_run_before_start(mocker):
    with pytest.raises(
        AssertionError, match="KafkaHealthcheckService must be started before running"
    ):
        await KafkaHealthcheckService().run()


@pytest.mark.asyncio
async def test_is_initially_healthy(mocker):
    consumer = AsyncMock()
    consumer.__aiter__.return_value = [mocker.Mock(value=b"PING")]
    mocker.patch(
        "healthcheck.kafka_healthcheck.service.get_healthcheck_consumer",
        return_value=consumer,
    )

    producer = AsyncMock()
    mocker.patch(
        "healthcheck.kafka_healthcheck.service.get_healthcheck_producer",
        return_value=producer,
    )

    await KafkaHealthcheckService().start()
    assert KafkaHealthcheckService().is_healthy()


@pytest.mark.asyncio
async def test_is_initially_non_critical_failure(mocker):
    consumer = AsyncMock()
    consumer.__aiter__.return_value = [mocker.Mock(value=b"PING")]
    mocker.patch(
        "healthcheck.kafka_healthcheck.service.get_healthcheck_consumer",
        return_value=consumer,
    )

    producer = AsyncMock()
    mocker.patch(
        "healthcheck.kafka_healthcheck.service.get_healthcheck_producer",
        return_value=producer,
    )

    await KafkaHealthcheckService().start()
    assert not KafkaHealthcheckService().is_critical_failure()


@pytest.mark.asyncio
async def test_is_unhealthy_after_tolerance(mocker):
    consumer = AsyncMock()
    consumer.__aiter__.return_value = [mocker.Mock(value=b"PING")]
    mocker.patch(
        "healthcheck.kafka_healthcheck.service.get_healthcheck_consumer",
        return_value=consumer,
    )

    producer = AsyncMock()
    mocker.patch(
        "healthcheck.kafka_healthcheck.service.get_healthcheck_producer",
        return_value=producer,
    )

    with freeze_time(datetime.now()) as frozen_time:
        await KafkaHealthcheckService().start()

        frozen_time.tick(
            delta=timedelta(seconds=settings.KAFKA_HEALTHCHECK_TOLERANCE_SECONDS)
        )

        assert not KafkaHealthcheckService().is_healthy()


@pytest.mark.asyncio
async def test_is_critical_failure_after_tolerance(mocker):
    consumer = AsyncMock()
    mocker.patch(
        "healthcheck.kafka_healthcheck.service.get_healthcheck_consumer",
        return_value=consumer,
    )

    producer = AsyncMock()
    mocker.patch(
        "healthcheck.kafka_healthcheck.service.get_healthcheck_producer",
        return_value=producer,
    )

    with freeze_time(datetime.now()) as frozen_time:
        await KafkaHealthcheckService().start()

        frozen_time.tick(
            delta=timedelta(
                minutes=settings.KAFKA_HEALTHCHECK_MAXIMUM_TOLERANCE_MINUTES,
                seconds=KafkaHealthcheckService.random_backoff_seconds,
            )
        )

        assert KafkaHealthcheckService().is_critical_failure()


@pytest.mark.asyncio
async def test_start(mocker):
    get_consumer = mocker.patch(
        "healthcheck.kafka_healthcheck.service.get_healthcheck_consumer"
    )

    get_producer = mocker.patch(
        "healthcheck.kafka_healthcheck.service.get_healthcheck_producer"
    )

    assert KafkaHealthcheckService().stopped is True

    await KafkaHealthcheckService().start()

    assert KafkaHealthcheckService().stopped is False
    get_consumer.assert_called_once()
    get_producer.assert_called_once()


@pytest.mark.asyncio
async def test_stop(mocker):
    task = mocker.Mock()
    task.done.return_value = False
    consumer = AsyncMock()
    mocker.patch(
        "healthcheck.kafka_healthcheck.service.get_healthcheck_consumer",
        return_value=consumer,
    )

    producer = AsyncMock()
    mocker.patch(
        "healthcheck.kafka_healthcheck.service.get_healthcheck_producer",
        return_value=producer,
    )
    KafkaHealthcheckService().task = task

    await KafkaHealthcheckService().start()
    await KafkaHealthcheckService().stop()

    assert KafkaHealthcheckService().stopped is True
    task.cancel.assert_called_once()
    consumer.stop.assert_awaited_once()
    producer.stop.assert_awaited_once()


@pytest.mark.asyncio
async def test_flush_without_starting(mocker):
    with pytest.raises(
        AssertionError, match="KafkaHealthcheckService must be started before flushing"
    ):
        await KafkaHealthcheckService().flush()


@pytest.mark.asyncio
async def test_flush(mocker):
    mocker.patch("healthcheck.kafka_healthcheck.service.get_healthcheck_consumer")
    producer = AsyncMock()
    mocker.patch(
        "healthcheck.kafka_healthcheck.service.get_healthcheck_producer",
        return_value=producer,
    )

    await KafkaHealthcheckService().start()

    await KafkaHealthcheckService().flush()

    producer.flush.assert_awaited_once()


@pytest.mark.asyncio
async def test_run(mocker):
    mocker.patch("healthcheck.kafka_healthcheck.service.get_healthcheck_consumer")
    mocker.patch("healthcheck.kafka_healthcheck.service.get_healthcheck_producer")
    KafkaHealthcheckService().ping = AsyncMock()
    KafkaHealthcheckService().pong = AsyncMock()

    await KafkaHealthcheckService().start()
    await KafkaHealthcheckService().run()

    KafkaHealthcheckService().ping.assert_awaited_once()
    KafkaHealthcheckService().pong.assert_awaited_once()
