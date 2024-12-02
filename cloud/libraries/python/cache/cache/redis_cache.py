import functools
import hashlib
import pickle
from typing import Any, Callable

from loguru import logger
from redis.client import Redis
from redis.exceptions import AuthenticationError, ConnectionError, RedisError
from starlette.requests import Request

from cache.settings import settings


class RedisCache:
    client: Redis
    _instance = None

    def __new__(cls) -> "RedisCache":
        if not cls._instance:
            cls._instance = super().__new__(cls)
            cls._instance.client = cls.get_redis()
        return cls._instance

    @staticmethod
    def get_redis() -> Redis:
        host = settings.REDIS_HOST
        port = settings.REDIS_PORT
        if settings.ENVIRONMENT == "local":
            url = f"redis://{host}:{port}"
        else:
            username = settings.REDIS_USERNAME.get_secret_value()
            password = settings.REDIS_PASSWORD.get_secret_value()

            url = f"redis://{username}:{password}@{host}:{port}"

        client = Redis.from_url(url=url, decode_responses=False)
        return client

    @property
    def connected(self):
        return self.check_connection()

    def check_connection(self):
        try:
            if self.client.ping():
                return True
            else:
                logger.error("Redis: Server did not respond ping")
        except AuthenticationError:
            logger.exception("Redis: Authentication error")
        except (ConnectionError, RedisError):
            logger.exception("Redis: Could not connect")

        return False

    def get(self, key: str, parse: bool = True) -> Any:
        value = self.client.get(key)
        if not parse:
            return value
        elif value:
            return pickle.loads(value)
        return None

    def scan(self, pattern: str):
        return self.client.scan_iter(match=pattern)

    def set(self, key: str, value: Any, ttl: int = settings.REDIS_CACHE_TTL) -> None:
        if value:
            self.client.set(name=key, value=pickle.dumps(value), ex=ttl)

    def delete(self, key):
        self.client.delete(key)


def get_cache_key(name: str, request: Request) -> str:
    hash_request_data = hashlib.sha1(f"{request.url.path}:{request.url.query}".encode()).hexdigest()
    return f"{settings.PROJECT_NAME}:{name}:{hash_request_data}"


def add_cache(name: str):
    cache = RedisCache()

    def decorator(func: Callable):
        @functools.wraps(func)
        async def wrapper(request: Request, *args, **kwargs):
            if not settings.CACHE_ENABLED or not cache.connected:
                response = await func(request, *args, **kwargs)
                return response

            cache_key = get_cache_key(name, request)
            if not (response := cache.get(cache_key)):
                response = await func(request, *args, **kwargs)
                cache.set(cache_key, response)
            return response

        return wrapper

    return decorator


def remove_cache(name: str):
    cache = RedisCache()

    def decorator(func: Callable):
        @functools.wraps(func)
        async def wrapper(*args, **kwargs):
            result = await func(*args, **kwargs)

            if not settings.CACHE_ENABLED or not cache.connected:
                return result

            for key in cache.scan(f"{settings.PROJECT_NAME}:{name}:*"):
                cache.delete(key)
            return result

        return wrapper

    return decorator


def remove_project_cache():
    cache = RedisCache()

    if settings.CACHE_ENABLED and cache.connected:
        for key in cache.scan(f"{settings.PROJECT_NAME}:*"):
            cache.delete(key)
        logger.info(f"{settings.PROJECT_NAME} cache cleaned")
    else:
        logger.info("Cache not enabled")


def add_lock(name: str, request: Request):
    cache = RedisCache()
    cache_key = get_cache_key(name, request)
    cache.set(cache_key, pickle.dumps({"locked": True}))


def remove_lock(name: str, request: Request):
    cache = RedisCache()
    cache_key = get_cache_key(name, request)
    cache.delete(cache_key)
