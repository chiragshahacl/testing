from unittest.mock import MagicMock, patch

import pytest
from confluent_kafka.admin import ClusterMetadata, ConfigResource, TopicMetadata
from confluent_kafka.cimpl import NewTopic

from app.common.kafka_admin import (
    KafkaAdminClientFactory,
    change_topic_retention,
    create_topic,
    get_topic_metadata,
)


@patch("app.common.kafka_admin.AdminClient")
def test_singleton_instance(mock_admin_client):
    mock_admin_client.return_value = MagicMock()
    KafkaAdminClientFactory._instance = None

    factory1 = KafkaAdminClientFactory()
    factory2 = KafkaAdminClientFactory()

    assert factory1 is factory2
    mock_admin_client.assert_called_once_with(
        {"bootstrap.servers": "localhost:9092", "client.id": "config-ms"}
    )


@patch("app.common.kafka_admin.AdminClient")
def test_admin_client_configuration(mock_admin_client):
    mock_admin_client.return_value = MagicMock()
    KafkaAdminClientFactory._instance = None

    factory = KafkaAdminClientFactory()

    assert factory.admin_client is not None
    assert factory.admin_client == mock_admin_client.return_value


@patch("app.common.kafka_admin.KafkaAdminClientFactory")
def test_get_config_topic_metadata(mock_kafka_admin_client_factory):
    mock_topic_metadata = MagicMock(spec=TopicMetadata)
    mock_cluster_metadata = MagicMock(spec=ClusterMetadata)

    config_topic_name = "test_topic"
    mock_cluster_metadata.topics = {config_topic_name: mock_topic_metadata}

    mock_admin_client = mock_kafka_admin_client_factory.return_value.admin_client
    mock_admin_client.list_topics.return_value = mock_cluster_metadata

    with patch("app.common.kafka_admin.config.PATIENT_VITALS_KAFKA_TOPIC_NAME", config_topic_name):
        result = get_topic_metadata(config_topic_name)
        assert result == mock_topic_metadata
        mock_admin_client.list_topics.assert_called_once()


@patch("app.common.kafka_admin.KafkaAdminClientFactory")
def test_get_config_topic_metadata_topic_not_found(mock_kafka_admin_client_factory):
    mock_cluster_metadata = MagicMock(spec=ClusterMetadata)
    mock_cluster_metadata.topics = {}

    mock_admin_client = mock_kafka_admin_client_factory.return_value.admin_client
    mock_admin_client.list_topics.return_value = mock_cluster_metadata

    with patch(
        "app.common.kafka_admin.config.PATIENT_VITALS_KAFKA_TOPIC_NAME", "non_existent_topic"
    ):
        result = get_topic_metadata("non_existent_topic")
        assert result is None
        mock_admin_client.list_topics.assert_called_once()


@patch("app.common.kafka_admin.KafkaAdminClientFactory")
@patch("app.common.kafka_admin.config")
def test_create_config_topic_success(mock_config, mock_kafka_admin_client_factory):
    mock_config.PATIENT_VITALS_KAFKA_TOPIC_NAME = "test_topic"
    mock_config.PATIENT_VITALS_KAFKA_TOPIC_PARTITIONS = 1
    mock_config.PATIENT_VITALS_KAFKA_TOPIC_REPLICATION_FACTOR = 1
    mock_config.PATIENT_VITALS_DEFAULT_KAFKA_TOPIC_RETENTION_MS = "60000"

    mock_future = MagicMock()
    mock_future.result.return_value = None

    mock_admin_client = mock_kafka_admin_client_factory.return_value.admin_client
    mock_admin_client.create_topics.return_value = {
        mock_config.PATIENT_VITALS_KAFKA_TOPIC_NAME: mock_future
    }

    create_topic(mock_config.PATIENT_VITALS_KAFKA_TOPIC_NAME)

    mock_admin_client.create_topics.assert_called_once_with(
        [
            NewTopic(
                topic="test_topic",
                num_partitions=1,
                replication_factor=1,
                config={"retention.ms": "60000"},
            )
        ],
        validate_only=False,
    )
    mock_future.result.assert_called_once()


@patch("app.common.kafka_admin.KafkaAdminClientFactory")
@patch("app.common.kafka_admin.config")
def test_create_config_topic_failure(mock_config, mock_kafka_admin_client_factory):
    mock_config.PATIENT_VITALS_KAFKA_TOPIC_NAME = "test_topic"
    mock_config.PATIENT_VITALS_KAFKA_TOPIC_PARTITIONS = 1
    mock_config.PATIENT_VITALS_KAFKA_TOPIC_REPLICATION_FACTOR = 1
    mock_config.PATIENT_VITALS_DEFAULT_KAFKA_TOPIC_RETENTION_MS = "60000"

    mock_future = MagicMock()
    mock_future.result.side_effect = Exception("Topic creation failed")

    mock_admin_client = mock_kafka_admin_client_factory.return_value.admin_client
    mock_admin_client.create_topics.return_value = {
        mock_config.PATIENT_VITALS_KAFKA_TOPIC_NAME: mock_future
    }

    with pytest.raises(Exception, match="Topic creation failed"):
        create_topic(mock_config.PATIENT_VITALS_KAFKA_TOPIC_NAME)

    mock_admin_client.create_topics.assert_called_once_with(
        [
            NewTopic(
                topic="test_topic",
                num_partitions=1,
                replication_factor=1,
                config={"retention.ms": "60000"},
            )
        ],
        validate_only=False,
    )
    mock_future.result.assert_called_once()


@patch("app.common.kafka_admin.KafkaAdminClientFactory")
@patch("app.common.kafka_admin.config")
def test_change_config_topic_retention_success(mock_config, mock_kafka_admin_client_factory):
    mock_config.PATIENT_VITALS_KAFKA_TOPIC_NAME = "test_topic"

    mock_future = MagicMock()
    mock_future.result.return_value = None

    mock_admin_client = mock_kafka_admin_client_factory.return_value.admin_client
    mock_admin_client.alter_configs.return_value = {
        mock_config.PATIENT_VITALS_KAFKA_TOPIC_NAME: mock_future
    }

    change_topic_retention(mock_config.PATIENT_VITALS_KAFKA_TOPIC_NAME, 60000)

    mock_admin_client.alter_configs.assert_called_once_with(
        resources=[
            ConfigResource(
                restype="TOPIC",
                name="test_topic",
                set_config={"retention.ms": "60000"},
                described_configs=None,
                error=None,
            )
        ],
        validate_only=False,
    )
    mock_future.result.assert_called_once()


@patch("app.common.kafka_admin.KafkaAdminClientFactory")
@patch("app.common.kafka_admin.config")
def test_change_config_topic_retention_failure(mock_config, mock_kafka_admin_client_factory):
    mock_config.PATIENT_VITALS_KAFKA_TOPIC_NAME = "test_topic"

    mock_future = MagicMock()
    mock_future.result.side_effect = Exception("Retention update failed")

    mock_admin_client = mock_kafka_admin_client_factory.return_value.admin_client
    mock_admin_client.alter_configs.return_value = {
        mock_config.PATIENT_VITALS_KAFKA_TOPIC_NAME: mock_future
    }

    with pytest.raises(Exception, match="Retention update failed"):
        change_topic_retention(mock_config.PATIENT_VITALS_KAFKA_TOPIC_NAME, 60000)

    mock_admin_client.alter_configs.assert_called_once_with(
        resources=[
            ConfigResource(
                restype="TOPIC",
                name="test_topic",
                set_config={"retention.ms": "60000"},
                described_configs=None,
                error=None,
            )
        ],
        validate_only=False,
    )
    mock_future.result.assert_called_once()
