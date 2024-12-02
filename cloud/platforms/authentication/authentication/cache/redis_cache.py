import logging
import pickle
import uuid
from datetime import datetime
from typing import Any

from django.conf import settings
from redis.client import Redis
from redis.exceptions import AuthenticationError, RedisError
from redis.exceptions import ConnectionError as RedisConnectionError

logger = logging.getLogger(__name__)


class RedisCache:
    client: Redis
    _instance = None

    def __new__(cls) -> Redis:
        if not cls._instance:
            cls._instance = super().__new__(cls)
            cls._instance.client = cls.get_redis()
        return cls._instance

    @staticmethod
    def get_redis() -> Redis:
        host_port = f"{settings.REDIS.get('HOST')}:{settings.REDIS.get('PORT')}"
        if settings.ENVIRONMENT == "local":
            url = f"redis://{host_port}"
        else:
            user_pass = f"{settings.REDIS.get('USERNAME')}:{settings.REDIS.get('PASSWORD')}"
            url = f"redis://{user_pass}@{host_port}"

        client = Redis.from_url(url=url, decode_responses=False)
        return client

    @property
    def connected(self):
        return self.check_connection()

    def check_connection(self):
        try:
            if self.client.ping():
                return True

            logger.error("Redis: Server did not respond ping")
        except AuthenticationError:
            logger.exception("Redis: Authentication error")
        except (RedisConnectionError, RedisError):
            logger.exception("Redis: Could not connect")

        return False

    def get(self, key: str) -> Any:
        value = self.client.get(key)
        if value:
            return pickle.loads(value)

        return None

    def scan(self, pattern: str):
        return self.client.scan_iter(match=pattern)

    def set(self, key: str, value: Any, ttl: int = settings.BRUTE_FORCE_ATTEMPT_TTL) -> None:
        if value:
            self.client.set(name=key, value=pickle.dumps(value), ex=ttl)

    def delete(self, key):
        self.client.delete(key)


def add_failed_authentication_attempt(username: str):
    client = RedisCache()
    if not settings.BRUTE_FORCE_PROTECTION_ENABLED or not client.connected:
        return

    unique_identifier = uuid.uuid4()
    key = f"{settings.PROJECT_NAME}:{username}:authentication_attempt_fail:{unique_identifier}"
    timestamp = datetime.now().timestamp()
    client.set(key, timestamp, ttl=settings.BRUTE_FORCE_ATTEMPT_TTL)


def count_failed_authentication_attempts(username: str) -> int:
    client = RedisCache()

    if not settings.BRUTE_FORCE_PROTECTION_ENABLED or not client.connected:
        return 0

    count = 0
    pattern = f"{settings.PROJECT_NAME}:{username}:authentication_attempt_fail:*"
    for _ in client.scan(pattern):
        count += 1

    return count


def block_account_temporarily(username: str):
    client = RedisCache()

    if not settings.BRUTE_FORCE_PROTECTION_ENABLED or not client.connected:
        return

    key = f"{settings.PROJECT_NAME}:{username}:account_blocked"
    timestamp = datetime.now().timestamp()
    time_blocked_in_seconds = settings.AUTHENTICATION_ACCOUNT_LOCKOUT_IN_MINUTES * 60
    client.set(key, timestamp, ttl=time_blocked_in_seconds)


def is_account_blocked(username: str) -> bool:
    client = RedisCache()

    if not settings.BRUTE_FORCE_PROTECTION_ENABLED or not client.connected:
        return False

    key = f"{settings.PROJECT_NAME}:{username}:account_blocked"

    is_blocked = bool(client.get(key))

    return is_blocked


def delete_app_settings() -> None:
    client = RedisCache()

    cache_key = f"{settings.PROJECT_NAME}:configuration"

    client.delete(cache_key)


def save_app_settings(value: str) -> None:
    client = RedisCache()

    cache_key = f"{settings.PROJECT_NAME}:configuration"

    client.set(cache_key, value, None)


def get_app_settings():
    client = RedisCache()

    cache_key = f"{settings.PROJECT_NAME}:configuration"

    return client.get(cache_key)
