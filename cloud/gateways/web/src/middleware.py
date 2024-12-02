from uuid import uuid4

from sentry_sdk import configure_scope, push_scope
from starlette.requests import Request


class CorrelationIDMiddleware:
    """Set Sentry's event correlation ID as the current correlation ID.

    The correlation ID is displayed in a Sentry event's detail view,
    which makes it easier to correlate logs to specific events.
    """

    def __init__(self, app):
        self.app = app

    async def __call__(self, scope, receive, send):
        if scope["type"] == "http":
            request = Request(scope)
            correlation_id = request.headers.get("x-correlation-id", str(uuid4()))
            request.state.correlation_id = correlation_id
            with push_scope() as sentry_scope:
                configure_scope(
                    lambda new_scope: sentry_scope.set_tag("correlation_id", correlation_id)
                )
        await self.app(scope, receive, send)
