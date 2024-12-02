from healthcheck.kafka_healthcheck.ssl import get_ssl_context
from healthcheck.settings import settings


def test_get_ssl_context(mocker):
    create_ssl_context = mocker.patch(
        "healthcheck.kafka_healthcheck.ssl.create_ssl_context"
    )

    get_ssl_context()

    create_ssl_context.assert_called_once_with(
        cafile=settings.KAFKA_CA_FILE_PATH,
        certfile=settings.KAFKA_CERT_FILE_PATH,
        keyfile=settings.KAFKA_KEY_FILE_PATH,
        password=settings.KAFKA_PASSWORD.get_secret_value(),
    )
