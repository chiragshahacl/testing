"""
ASGI config for mysite project.

It exposes the ASGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/4.1/howto/deployment/asgi/
"""

import environ
from django.core.asgi import get_asgi_application

env = environ.Env()
# Retrieve environment variables from .env file
environ.Env.read_env(".env")

env.str("DJANGO_SETTINGS_MODULE", "authentication.settings")

application = get_asgi_application()
