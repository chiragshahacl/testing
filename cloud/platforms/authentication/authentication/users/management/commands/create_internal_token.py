import secrets
from datetime import datetime, timedelta

import jwt
from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand

from authentication import settings

User = get_user_model()


class Command(BaseCommand):
    help = "Creates a token to be used for internal communication"

    def add_arguments(self, parser):
        parser.add_argument("--duration-days", help="Duration of the token", type=int)

    def handle(self, *args, **kwargs):
        user_id = User.objects.get(email=settings.DEFAULT_ADMIN_USERNAME).id
        now = datetime.now()
        duration_days = kwargs["duration_days"]
        exp = now + timedelta(days=duration_days)
        payload = {
            "token_type": "access",
            "iat": int(now.timestamp()),
            "exp": int(exp.timestamp()),
            "jti": secrets.token_hex(16),
            "user_id": str(user_id),
            "username": settings.DEFAULT_ADMIN_USERNAME,
            "tenant_id": "sibel",
            "groups": ["admin"],
            "aud": "tucana",
        }
        token = jwt.encode(payload, settings.SIMPLE_JWT["SIGNING_KEY"], algorithm="RS256")
        return token
