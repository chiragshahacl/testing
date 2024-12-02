import fakeredis
import pytest
from cache import RedisCache


@pytest.fixture()
def fake_cache(mocker):
    fredis = fakeredis.FakeRedis(decode_responses=False)
    with mocker.patch.object(RedisCache(), "client", fredis):
        yield


@pytest.fixture(autouse=True)
def mock_redis(mocker):
    mock_redis = mocker.patch("cache.redis_cache.Redis")
    yield mock_redis
