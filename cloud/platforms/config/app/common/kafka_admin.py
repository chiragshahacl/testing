from typing import Optional

from aiokafka.cluster import ClusterMetadata
from confluent_kafka.admin import AdminClient, ConfigResource, TopicMetadata
from confluent_kafka.cimpl import NewTopic
from loguru import logger

from app.settings import config


def get_kafka_connection_params() -> dict[str, str]:
    url = f"{config.KAFKA_HOST}:{config.KAFKA_PORT}"
    conn_params = {
        "bootstrap.servers": url,
        "client.id": config.KAFKA_CLIENT_ID,
    }
    if config.DEBUG:
        conn_params["debug"] = "broker,admin,protocol"
    if config.ENVIRONMENT != "local":
        conn_params = {
            "bootstrap.servers": url,
            "client.id": "config-ms",
            "security.protocol": "SSL",
            "ssl.ca.location": config.KAFKA_CA_FILE_PATH,
            "ssl.certificate.location": config.KAFKA_CERT_FILE_PATH,
            "ssl.key.location": config.KAFKA_KEY_FILE_PATH,
            "ssl.key.password": config.KAFKA_PASSWORD.get_secret_value(),
            **conn_params,
        }
    return conn_params


class KafkaAdminClientFactory:
    _instance = None

    def __new__(cls, *args, **kwargs):
        if not cls._instance:
            cls._instance = super(KafkaAdminClientFactory, cls).__new__(cls, *args, **kwargs)
            cls._instance.admin_client = AdminClient(get_kafka_connection_params())
        return cls._instance


def get_topic_metadata(topic_name: str) -> Optional[TopicMetadata]:
    cluster: ClusterMetadata = KafkaAdminClientFactory().admin_client.list_topics()
    topics: dict[str, TopicMetadata] = cluster.topics
    return topics.get(topic_name)


def create_topic(topic_name: str):
    fs = KafkaAdminClientFactory().admin_client.create_topics(
        [
            NewTopic(
                topic=topic_name,
                num_partitions=config.PATIENT_VITALS_KAFKA_TOPIC_PARTITIONS,
                replication_factor=config.PATIENT_VITALS_KAFKA_TOPIC_REPLICATION_FACTOR,
                config={
                    "retention.ms": config.PATIENT_VITALS_DEFAULT_KAFKA_TOPIC_RETENTION_MS,
                },
            )
        ],
        validate_only=False,
    )
    for topic, f in fs.items():
        f.result()
        logger.info(f"Topic created: {topic}")


def change_topic_retention(topic_name: str, retention_ms: int):
    fs = KafkaAdminClientFactory().admin_client.alter_configs(
        resources=[
            ConfigResource(
                restype="TOPIC",
                name=topic_name,
                set_config={"retention.ms": str(retention_ms)},
                described_configs=None,
                error=None,
            )
        ],
        validate_only=False,
    )
    for topic, f in fs.items():
        f.result()
        logger.info(f"Retention updated: {topic}")
