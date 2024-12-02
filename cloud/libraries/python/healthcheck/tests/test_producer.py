import pytest
from healthcheck.kafka_healthcheck.producer import get_healthcheck_producer


@pytest.mark.asyncio
@pytest.mark.parametrize("environment", ["local", "prod"])
async def test_get_producer(mocker, environment):
    kafka_producer = mocker.patch(
        "healthcheck.kafka_healthcheck.producer.AIOKafkaProducer"
    )
    mocker.patch("healthcheck.kafka_healthcheck.producer.get_ssl_context")
    mocker.patch(
        "healthcheck.kafka_healthcheck.producer.settings.ENVIRONMENT", environment
    )

    kafka_producer.return_value.start = mocker.AsyncMock()

    await get_healthcheck_producer()

    kafka_producer.return_value.start.assert_awaited_once_with()
