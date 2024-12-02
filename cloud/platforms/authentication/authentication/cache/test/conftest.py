import fakeredis
import pytest

from authentication.cache.redis_cache import RedisCache


@pytest.fixture()
def fake_cache(mocker):
    fredis = fakeredis.FakeRedis(decode_responses=False)
    with mocker.patch.object(RedisCache(), "client", fredis):
        yield


@pytest.fixture(autouse=True)
def mock_redis(mocker):
    redis_mock = mocker.patch("authentication.cache.redis_cache.Redis")
    yield redis_mock
