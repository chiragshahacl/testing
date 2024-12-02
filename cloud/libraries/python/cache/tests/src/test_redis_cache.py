import pickle

import pytest
from cache import RedisCache, add_cache, remove_cache, remove_project_cache
from cache.settings import settings
from pydantic import SecretStr
from redis.exceptions import AuthenticationError, ConnectionError, RedisError


class FakeUrl:
    def __init__(self):
        self.path = "/fake/path"
        self.query = "?fake=query"


class FakeResponse:
    def __init__(self):
        self.headers = {}
        self.call_count = 0
        self.url = FakeUrl()

    def __call__(self, *args, **kwargs):
        self.call_count += 1
        return self


def test_get_redis_connection_url_local(mocker, mock_redis):
    mocker.patch.object(settings, "ENVIRONMENT", "local")
    mocker.patch.object(settings, "REDIS_HOST", "host")
    mocker.patch.object(settings, "REDIS_PORT", 1122)

    RedisCache.get_redis()

    mock_redis.from_url.assert_called_once_with(url="redis://host:1122", decode_responses=False)


def test_get_redis_connection_url_other(mocker, mock_redis):
    mocker.patch.object(settings, "ENVIRONMENT", "other")
    mocker.patch.object(settings, "REDIS_HOST", "host")
    mocker.patch.object(settings, "REDIS_PORT", 1122)
    mocker.patch.object(settings, "REDIS_USERNAME", SecretStr("user"))
    mocker.patch.object(settings, "REDIS_PASSWORD", SecretStr("pass"))

    RedisCache.get_redis()

    mock_redis.from_url.assert_called_once_with(
        url="redis://user:pass@host:1122", decode_responses=False
    )


def test_redis_cache_get(fake_cache, mock_redis):
    cache = RedisCache()
    cache.client = mock_redis()
    cache.client.get.return_value = pickle.dumps("value")
    cache.get("key")
    mock_redis.return_value.get.assert_called_once_with("key")


def test_redis_cache_scan(mock_redis):
    cache = RedisCache()
    cache.client = mock_redis()
    cache.scan("pattern")
    mock_redis.return_value.scan_iter.assert_called_once_with(match="pattern")


def test_redis_cache_set(mock_redis):
    cache = RedisCache()
    cache.client = mock_redis()
    cache.set("key", "value")
    mock_redis.return_value.set.assert_called_once_with(
        name="key", value=pickle.dumps("value"), ex=settings.REDIS_CACHE_TTL
    )


def test_redis_cache_delete(mock_redis):
    cache = RedisCache()
    cache.client = mock_redis()
    cache.delete("key")
    mock_redis.return_value.delete.assert_called_once_with("key")


@add_cache("/some-api")
async def get_function(x):
    return x()


@remove_cache("/some-api")
async def clear_function():
    pass


@pytest.mark.asyncio
async def test_with_cache_hit(mocker, fake_cache):
    mock_value = FakeResponse()
    await clear_function()

    await get_function(mock_value)
    await get_function(mock_value)

    assert mock_value.call_count == 1


@pytest.mark.asyncio
async def test_with_clear_hit(mocker, fake_cache):
    mock_value = FakeResponse()

    await clear_function()
    await get_function(mock_value)

    await clear_function()
    await get_function(mock_value)

    assert mock_value.call_count == 2


def test_cache_connected_at_startup():
    cache = RedisCache()
    assert cache.connected


@pytest.mark.parametrize(
    "exception",
    [
        AuthenticationError,
        ConnectionError,
        RedisError,
    ],
)
def test_cache_disconnects_on_exception(mocker, mock_redis, exception):
    cache = RedisCache()
    cache._instance.client.ping.side_effect = exception
    assert not cache.connected
    cache._instance.client.ping.reset_mock()


def test_cache_disconnects_on_ping_fail():
    cache = RedisCache()
    cache._instance.client.ping.return_value = False
    assert not cache.connected
    cache._instance.client.ping.reset_mock()


@pytest.mark.asyncio
async def test_cache_ignore_caches_if_not_connected(mocker):
    cache = RedisCache()
    cache._instance.client.ping.return_value = False

    mock_value = mocker.Mock(return_value=2)
    await get_function(mock_value)
    await get_function(mock_value)

    assert mock_value.call_count == 2
    cache._instance.client.ping.reset_mock()


def test_remove_project_cache(fake_cache, mock_redis):
    cache = RedisCache()
    cache.set("project_name_1:name:request_1", "value_1")
    cache.set("project_name_1:name:request_2", "value_2")
    cache.set("project_name_2:name:request_1", "value_1")
    settings.PROJECT_NAME = "project_name_1"
    remove_project_cache()
    assert not cache.get("project_name_1:name:request_1")
    assert not cache.get("project_name_1:name:request_2")
    assert cache.get("project_name_2:name:request_1")
