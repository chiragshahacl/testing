import ssl

from django.conf import settings
from kafka import KafkaProducer

from authentication.broker.publisher import PublisherBackend
from authentication.constants import LOCAL_ENVIRONMENT_NAME


class KafkaClientFactory:
    def __init__(self):
        self.client = None

    def __call__(self, *args, **kwargs):
        if not self.client:
            kafka_host = settings.KAFKA.get("HOST")
            kafka_port = settings.KAFKA.get("PORT")
            kafka_bootstrap_server = f"{kafka_host}:{kafka_port}"

            if settings.ENVIRONMENT == LOCAL_ENVIRONMENT_NAME:
                self.client = KafkaProducer(bootstrap_servers=kafka_bootstrap_server)
            else:
                ssl_context = ssl.create_default_context(
                    cafile=settings.KAFKA.get("KAFKA_CA_FILE_PATH")
                )
                ssl_context.load_cert_chain(
                    certfile=settings.KAFKA.get("KAFKA_CERT_FILE_PATH"),
                    keyfile=settings.KAFKA.get("KAFKA_KEY_FILE_PATH"),
                    password=settings.KAFKA.get("KAFKA_PASSWORD"),
                )
                self.client = KafkaProducer(
                    bootstrap_servers=[kafka_bootstrap_server],
                    security_protocol="SSL",
                    ssl_context=ssl_context,
                )

        return self.client


class KafkaPublisher(PublisherBackend):
    KafkaClient = KafkaClientFactory()

    def notify(
        self,
        entity_id: str,
        event_name: str,
        performed_by: str,
    ) -> None:
        client = self.KafkaClient()
        schema = self.get_schema(entity_id, event_name, performed_by)
        topic = settings.KAFKA.get("TOPICS").get("AUDIT")
        message = str.encode(schema.model_dump_json())

        client.send(topic, message)
        client.flush()
