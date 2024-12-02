from src.cache import MetricsCacheService
from src.common.enums import HeaderEventTypes
from src.health_check.api import api as health_check_api
from src.main import (
    BROADCAST_TOPICS,
    NOTIFY_TOPICS,
    create_app,
    register_event_listeners,
)
from src.realtime.subscriber import ConnectionManager
from src.settings import config
from src.streams import EventSubscriber


def test_endpoints_starts_with_base_path(test_app):
    for route in test_app.app.routes:
        if not route.path.startswith("/health"):
            assert route.path.startswith(config.BASE_PATH)


def test_health_api_is_added_with_no_base_path(mocker):
    app_mock = mocker.patch("src.main.FastAPI").return_value

    result = create_app()

    assert result is app_mock
    assert mocker.call(health_check_api) in app_mock.include_router.mock_calls


def test_register_event_listeners():
    sub_manager = ConnectionManager()
    event_subscriber = EventSubscriber()
    cache_service = MetricsCacheService()

    register_event_listeners()

    for topic in BROADCAST_TOPICS:
        handlers = event_subscriber._key_handlers[topic]
        assert sub_manager.broadcast in handlers

    for topic in NOTIFY_TOPICS:
        handlers = event_subscriber._key_handlers[topic]
        assert sub_manager.notify in handlers

    assert (
        cache_service.new_metrics_handler
        in event_subscriber._key_handlers[HeaderEventTypes.NEW_METRICS]
    )

    sub_manager.reset()
    cache_service.reset()
    event_subscriber.reset()
