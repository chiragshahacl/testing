import pytest
from aiokafka import AIOKafkaProducer

from app.common.event_sourcing.publisher import KafkaProducerClientFactory
from app.settings import config


class TestKafkaClientFactory:
    def test_init(self):
        factory = KafkaProducerClientFactory()

        assert factory.client is None

    @pytest.mark.asyncio
    async def test_call_local_env(self, mocker):
        factory = KafkaProducerClientFactory()
        mocker.patch.object(config, "ENVIRONMENT", "local")
        consumer_mock = mocker.AsyncMock(spec=AIOKafkaProducer)
        aio_producer_mock = mocker.patch(
            "app.common.event_sourcing.publisher.AIOKafkaProducer",
            return_value=consumer_mock,
        )

        client = await factory()

        aio_producer_mock.assert_called_once_with(
            bootstrap_servers=f"{config.KAFKA_HOST}:{config.KAFKA_PORT}",
        )
        assert client is aio_producer_mock.return_value

    @pytest.mark.asyncio
    async def test_call_non_local_env(self, mocker):
        factory = KafkaProducerClientFactory()
        mocker.patch.object(config, "ENVIRONMENT", "other")
        consumer_mock = mocker.AsyncMock(spec=AIOKafkaProducer)
        consumer_mock.start = mocker.AsyncMock()
        aio_producer_mock = mocker.patch(
            "app.common.event_sourcing.publisher.AIOKafkaProducer",
            return_value=consumer_mock,
        )
        create_ssl_context_mock = mocker.patch(
            "app.common.event_sourcing.publisher.create_ssl_context"
        )

        client = await factory()

        create_ssl_context_mock.assert_called_once_with(
            cafile=config.KAFKA_CA_FILE_PATH,
            certfile=config.KAFKA_CERT_FILE_PATH,
            keyfile=config.KAFKA_KEY_FILE_PATH,
            password=config.KAFKA_PASSWORD.get_secret_value(),
        )
        aio_producer_mock.assert_called_once_with(
            bootstrap_servers=f"{config.KAFKA_HOST}:{config.KAFKA_PORT}",
            security_protocol="SSL",
            ssl_context=create_ssl_context_mock.return_value,
        )
        assert client is aio_producer_mock.return_value
