# pylint: skip-file

import pickle

import pytest
from django.conf import settings
from redis.exceptions import AuthenticationError, ConnectionError, RedisError

from authentication.cache.redis_cache import RedisCache


def test_get_redis_connection_url_local(mocker, mock_redis):
    mocker.patch.object(settings, "ENVIRONMENT", "local")
    mocker.patch.object(settings, "REDIS", {"HOST": "host", "PORT": 1122})

    RedisCache.get_redis()

    mock_redis.from_url.assert_called_once_with(url="redis://host:1122", decode_responses=False)


def test_get_redis_connection_url_other(mocker, mock_redis):
    mocker.patch.object(settings, "ENVIRONMENT", "other")
    mocker.patch.object(
        settings,
        "REDIS",
        {"HOST": "host", "PORT": 1122, "USERNAME": "user", "PASSWORD": "pass"},
    )

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
        name="key", value=pickle.dumps("value"), ex=settings.BRUTE_FORCE_ATTEMPT_TTL
    )


def test_redis_cache_delete(mock_redis):
    cache = RedisCache()
    cache.client = mock_redis()
    cache.delete("key")
    mock_redis.return_value.delete.assert_called_once_with("key")


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
def test_cache_disconects_on_exception(mock_redis, exception):
    cache = RedisCache()
    cache._instance.client.ping.side_effect = exception
    assert not cache.connected
    cache._instance.client.ping.reset_mock()


def test_cache_disconects_on_ping_fail():
    cache = RedisCache()
    cache._instance.client.ping.return_value = False
    assert not cache.connected
    cache._instance.client.ping.reset_mock()


def test_redis_check_connection_ping_false(mocker, mock_redis):
    cache = RedisCache()
    cache.client = mock_redis()
    cache._instance.client.ping.return_value = False
    assert not cache.connected
    cache._instance.client.ping.reset_mock()
