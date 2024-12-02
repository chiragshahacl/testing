from aiokafka.helpers import create_ssl_context

from healthcheck.settings import settings


def get_ssl_context():
    return create_ssl_context(
        cafile=settings.KAFKA_CA_FILE_PATH,
        certfile=settings.KAFKA_CERT_FILE_PATH,
        keyfile=settings.KAFKA_KEY_FILE_PATH,
        password=settings.KAFKA_PASSWORD.get_secret_value(),
    )
