import importlib
from unittest import mock

import fakeredis
import respx
from behave import fixture, use_fixture
from starlette.testclient import TestClient

import cache
import src.device.api
from src.consumer import KafkaConsumerFactory
from src.event_sourcing.publisher import KafkaProducerFactory
from src.main import create_app
from src.settings import settings


@fixture
def create_test_client(context):
    app = create_app()
    with respx.mock:
        context.client = TestClient(app, raise_server_exceptions=True)
        yield context.client


@fixture
def create_command_disabled_test_client(context, scenario):
    settings_mock = mock.patch.object(settings, "PM_COMMAND_EXECUTION_ENABLED", False)
    settings_mock.start()
    importlib.reload(src.device.api)
    importlib.reload(src.main)
    app = create_app()
    respx.mock.start()
    context.client = TestClient(app, raise_server_exceptions=True)
    yield
    settings_mock.stop()
    importlib.reload(src.device.api)
    importlib.reload(src.main)
    respx.mock.stop()


@fixture
def mock_consumer(_):
    kafka_consumer_mock = mock.AsyncMock()
    with mock.patch.object(KafkaConsumerFactory, "__call__", return_value=kafka_consumer_mock):
        yield


@fixture
def mock_producer(context):
    kafka_producer_mock = mock.AsyncMock()
    with mock.patch.object(
        KafkaProducerFactory,
        "__call__",
        return_value=kafka_producer_mock,
    ):
        kafka_producer_mock.start = mock.AsyncMock()
        kafka_producer_mock.send_and_wait = mock.AsyncMock()
        kafka_producer_mock.stop = mock.AsyncMock()
        context.producer = kafka_producer_mock
        yield


@fixture
def fake_redis(context):
    fredis = fakeredis.FakeRedis(decode_responses=False)
    with mock.patch.object(cache.RedisCache(), "client", fredis):
        context.cache = fredis
        yield


@fixture
def clean_cache(context):
    context.cache.flushdb()


@fixture
def patch_command_organizer(context):
    context.patcher = mock.patch("src.device.command_organizer.CommandOrganizer.check_for_response")
    context.mock_check_for_response = context.patcher.start()
    yield
    context.patcher.stop()


def before_all(context):
    use_fixture(mock_consumer, context)
    use_fixture(fake_redis, context)


def before_scenario(context, scenario):
    if "disable_command_exec" in scenario.tags:
        use_fixture(create_command_disabled_test_client, context, scenario)
    else:
        use_fixture(create_test_client, context)
    use_fixture(clean_cache, context)
    use_fixture(mock_producer, context)
    use_fixture(patch_command_organizer, context)
