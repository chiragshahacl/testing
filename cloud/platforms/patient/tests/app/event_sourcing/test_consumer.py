import pytest
from aiokafka import AIOKafkaConsumer

from app.consumer import KafkaConsumerClientFactory
from app.settings import config


class TestKafkaClientFactory:
    def test_init(self):
        factory = KafkaConsumerClientFactory()

        assert factory.client is None

    @pytest.mark.asyncio
    async def test_call_local_env(self, mocker):
        factory = KafkaConsumerClientFactory()
        mocker.patch.object(config, "ENVIRONMENT", "local")
        consumer_mock = mocker.AsyncMock(spec=AIOKafkaConsumer)
        aio_consumer_mock = mocker.patch(
            "app.consumer.AIOKafkaConsumer", return_value=consumer_mock
        )

        client = await factory()

        aio_consumer_mock.assert_called_once_with(
            config.EVENTS_ALERT_TOPIC,
            config.EVENTS_DEVICE_TOPIC,
            config.EVENTS_SDC_TOPIC,
            config.PATIENT_PUBLISHER_AUDIT_TRAIL_STREAM_NAME,
            group_id=config.CONSUMER_PATIENT_GROUP_ID,
            bootstrap_servers=f"{config.KAFKA_HOST}:{config.KAFKA_PORT}",
            retry_backoff_ms=config.KAFKA_RETRY_BACKOFF,
            metadata_max_age_ms=config.KAFKA_METADATA_MAX_AGE,
        )
        assert client is aio_consumer_mock.return_value

    @pytest.mark.asyncio
    async def test_call_non_local_env(self, mocker):
        factory = KafkaConsumerClientFactory()
        mocker.patch.object(config, "ENVIRONMENT", "other")
        consumer_mock = mocker.AsyncMock(spec=AIOKafkaConsumer)
        consumer_mock.start = mocker.AsyncMock()
        aio_consumer_mock = mocker.patch(
            "app.consumer.AIOKafkaConsumer", return_value=consumer_mock
        )
        create_ssl_context_mock = mocker.patch("app.consumer.create_ssl_context")

        client = await factory()

        create_ssl_context_mock.assert_called_once_with(
            cafile=config.KAFKA_CA_FILE_PATH,
            certfile=config.KAFKA_CERT_FILE_PATH,
            keyfile=config.KAFKA_KEY_FILE_PATH,
            password=config.KAFKA_PASSWORD.get_secret_value(),
        )
        aio_consumer_mock.assert_called_once_with(
            config.EVENTS_ALERT_TOPIC,
            config.EVENTS_DEVICE_TOPIC,
            config.EVENTS_SDC_TOPIC,
            config.PATIENT_PUBLISHER_AUDIT_TRAIL_STREAM_NAME,
            group_id=config.CONSUMER_PATIENT_GROUP_ID,
            bootstrap_servers=f"{config.KAFKA_HOST}:{config.KAFKA_PORT}",
            security_protocol="SSL",
            ssl_context=create_ssl_context_mock.return_value,
            retry_backoff_ms=config.KAFKA_RETRY_BACKOFF,
            metadata_max_age_ms=config.KAFKA_METADATA_MAX_AGE,
        )
        assert client is aio_consumer_mock.return_value
