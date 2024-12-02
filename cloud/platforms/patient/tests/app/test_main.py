import asyncio

import pytest

from app.common.utils import load_backend
from app.main import add_correlation_id, lifespan
from app.settings import config


def test_endpoints_starts_with_base_path(test_app):
    for route in test_app.app.routes:
        if not (route.path.startswith("/health") or route.path.startswith("/device")):
            assert route.path.startswith(config.BASE_PATH)


def test_load_backend(mocker) -> None:
    bad_path = "app.common.event_sourcing.publisher.BadKafkaProducerClientFactory"

    mocker.patch(
        "app.common.utils.load_backend",
        side_effect=[Exception(f"Path not found: {bad_path}")],
    )
    with pytest.raises(Exception):
        load_backend(bad_path)


@pytest.mark.asyncio
async def test_lifespan(mocker):
    consumer = mocker.AsyncMock()
    aiokafka_consumer_class_mock = mocker.patch("app.main.KafkaConsumerClient", consumer)
    aiokafka_consumer_class_mock.return_value.stop = mocker.AsyncMock()
    aiokafka_producer_class_mock = mocker.patch("app.main.KafkaProducerClient", mocker.AsyncMock())
    aiokafka_producer_class_mock.return_value.stop = mocker.AsyncMock()
    get_running_loop_mock = mocker.patch.object(asyncio, "get_running_loop")
    event_consumer = mocker.MagicMock()
    mocker.patch("app.main.event_consumer", event_consumer)
    healthcheck_instance = mocker.AsyncMock()
    mocker.patch("app.main.KafkaHealthcheckService", return_value=healthcheck_instance)

    async with lifespan(mocker.AsyncMock()):
        pass

    get_running_loop_mock.assert_called_once()
    healthcheck_instance.start.assert_called_once()
    healthcheck_instance.watchdog.assert_called_once()
    aiokafka_consumer_class_mock.assert_called_once()
    aiokafka_producer_class_mock.assert_called_once()
    aiokafka_producer_class_mock.return_value.stop.assert_awaited_once()
    aiokafka_consumer_class_mock.return_value.stop.assert_awaited_once()


@pytest.mark.asyncio
async def test_add_correlation_id(mocker):
    push_scope_mock = mocker.patch("app.main.push_scope")
    push_scope_mock.return_value.__enter__.return_value = mocker.MagicMock()
    configure_scope_mock = mocker.patch("app.main.configure_scope")
    scope_config_mock = mocker.patch("app.main.ScopeConfiguration", mocker.MagicMock())
    call_next_mock = mocker.AsyncMock()
    request_mock = mocker.MagicMock()
    request_mock.headers["x-correlation-id"] = "test-corr-id"
    await add_correlation_id(request_mock, call_next_mock)
    configure_scope_mock.assert_called_once_with(
        scope_config_mock(
            push_scope_mock.return_value.__enter__.return_value, "test-corr-id"
        ).return_value
    )
    call_next_mock.assert_called_once_with(request_mock)
