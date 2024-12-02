import pytest
from healthcheck.kafka_healthcheck.consumer import get_healthcheck_consumer


@pytest.mark.asyncio
@pytest.mark.parametrize("environment", ["local", "prod"])
async def test_get_consumer(mocker, environment):
    kafka_consumer = mocker.patch(
        "healthcheck.kafka_healthcheck.consumer.AIOKafkaConsumer"
    )
    mocker.patch("healthcheck.kafka_healthcheck.consumer.get_ssl_context")

    mocker.patch(
        "healthcheck.kafka_healthcheck.consumer.settings.ENVIRONMENT", environment
    )
    kafka_consumer.return_value.start = mocker.AsyncMock()

    await get_healthcheck_consumer()

    kafka_consumer.return_value.start.assert_awaited_once_with()
