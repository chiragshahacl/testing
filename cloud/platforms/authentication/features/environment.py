from unittest import mock

import fakeredis
from authentication.cache.redis_cache import RedisCache
from behave import fixture, use_fixture


@fixture
def mock_producer(context):
    kafka_client_mock = mock.MagicMock()
    with mock.patch(
        "authentication.users.signals.Publisher", return_value=kafka_client_mock
    ), mock.patch("authentication.config.signals.Publisher", return_value=kafka_client_mock):
        kafka_client_mock.notify = mock.Mock()
        context.publisher_mock = kafka_client_mock
        yield


@fixture
def fake_redis(context):
    fredis = fakeredis.FakeRedis(decode_responses=False)
    with mock.patch.object(RedisCache(), "client", fredis):
        context.cache = fredis
        yield


def before_all(context):
    use_fixture(mock_producer, context)
    use_fixture(fake_redis, context)
