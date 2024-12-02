from datetime import timedelta

from common.utils import load_backend
from django.contrib.auth import get_user_model
from django.utils import timezone

from authentication import settings
from authentication.cache.redis_cache import (
    add_failed_authentication_attempt,
    block_account_temporarily,
    count_failed_authentication_attempts,
    is_account_blocked,
)
from authentication.users.signals import publish_user_account_blocked

User = get_user_model()
Publisher = load_backend(settings.KAFKA.get("HANDLER_CLASS"))


def is_authentication_allowed(user: User) -> bool:
    # Check if user blocked in cache
    account_blocked_cache = is_account_blocked(user.email)
    # Check if blocked in DB
    account_blocked_db = user.blocked_until is not None and user.blocked_until >= timezone.now()

    return not (account_blocked_cache or account_blocked_db)


def authentication_failed_penalization(user: User):
    # Add failed attempt registry in Cache
    add_failed_authentication_attempt(user.email)

    # Check if account should be blocked
    tries_count = count_failed_authentication_attempts(user.email)
    if tries_count >= settings.AUTHENTICATION_FAILURE_THRESHOLD:
        block_account_temporarily(user.email)
        user.blocked_until = timezone.now() + timedelta(
            minutes=settings.AUTHENTICATION_ACCOUNT_LOCKOUT_IN_MINUTES
        )
        user.save()
        publish_user_account_blocked(user)

    # TODO: Calculate delay response time and waite # pylint: disable=W0511
