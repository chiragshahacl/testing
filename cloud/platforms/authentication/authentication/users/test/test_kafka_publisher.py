# pylint: skip-file
from unittest.mock import MagicMock, patch

import pytest

from authentication.broker.publisher_kafka import KafkaClientFactory, KafkaPublisher


@pytest.fixture
def mock_kafka_producer():
    return MagicMock()


@pytest.fixture
def mock_kafka_client_factory(mock_kafka_producer):
    with patch(
        "authentication.broker.publisher_kafka.KafkaClientFactory.__call__",
        return_value=mock_kafka_producer,
    ):
        yield


def test_kafka_publisher_notify(mock_kafka_client_factory, mock_kafka_producer):
    # Setup
    entity_id = "test_entity_id"
    event_name = "test_event_name"
    performed_by = "test_performed_by"

    # Execute
    publisher = KafkaPublisher()
    publisher.notify(entity_id, event_name, performed_by)

    # Assert
    topic = publisher.KafkaClient().send.call_args[0][0]
    message = publisher.KafkaClient().send.call_args[0][1]
    mock_kafka_producer.send.assert_called_once_with(topic, message)
    mock_kafka_producer.flush.assert_called_once()


def test_kafka_client_factory_call_local_environment(
    mock_kafka_producer,
):
    # Setup
    with patch(
        "authentication.broker.publisher_kafka.settings.ENVIRONMENT",
        "local",
    ), patch(
        "authentication.broker.publisher_kafka.KafkaProducer",
        return_value=mock_kafka_producer,
    ) as mock_kafka_producer_constructor:
        factory = KafkaClientFactory()

        # Execute
        result = factory()

        # Assert
        assert result == mock_kafka_producer
        mock_kafka_producer_constructor.assert_called_once_with(bootstrap_servers="localhost:9092")


def test_kafka_client_factory_call_remote_environment(
    mock_kafka_producer,
):
    # Setup
    with patch(
        "authentication.broker.publisher_kafka.settings.KAFKA",
        {
            "HOST": "kafka.example.com",
            "PORT": "9092",
            "KAFKA_CA_FILE_PATH": "/path/to/ca.crt",
            "KAFKA_CERT_FILE_PATH": "/path/to/cert.pem",
            "KAFKA_KEY_FILE_PATH": "/path/to/key.pem",
            "KAFKA_PASSWORD": "password",
            "TOPICS": {"AUDIT": "audit-topic"},
        },
    ), patch(
        "authentication.broker.publisher_kafka.settings.ENVIRONMENT",
        "production",
    ), patch(
        "authentication.broker.publisher_kafka.ssl.create_default_context"
    ) as mock_ssl_context_constructor:
        mock_ssl_context = MagicMock()
        mock_ssl_context_constructor.return_value = mock_ssl_context

        mock_load_cert_chain = MagicMock()
        mock_ssl_context.load_cert_chain = mock_load_cert_chain

        with patch(
            "authentication.broker.publisher_kafka.KafkaProducer",
            return_value=mock_kafka_producer,
        ) as mock_kafka_producer_constructor:
            factory = KafkaClientFactory()

            # Execute
            result = factory()

            # Assert
            assert result == mock_kafka_producer
            mock_kafka_producer_constructor.assert_called_once_with(
                bootstrap_servers=["kafka.example.com:9092"],
                security_protocol="SSL",
                ssl_context=mock_ssl_context,
            )
            mock_ssl_context_constructor.assert_called_once_with(cafile="/path/to/ca.crt")
            mock_load_cert_chain.assert_called_once_with(
                certfile="/path/to/cert.pem",
                keyfile="/path/to/key.pem",
                password="password",
            )
