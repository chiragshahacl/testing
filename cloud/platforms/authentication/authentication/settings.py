import base64
import os
from datetime import timedelta
from os.path import join
from pathlib import Path

import environ
import sentry_sdk
from sentry_sdk.integrations.django import DjangoIntegration

from authentication.constants import LOCAL_ENVIRONMENT_NAME

BASE_DIR = Path(__file__).resolve(strict=True).parent.parent


env = environ.Env()
# Retrieve environment variables from .env file
environ.Env.read_env(os.path.join(BASE_DIR, ".env"))

ENVIRONMENT = env.str("ENVIRONMENT", LOCAL_ENVIRONMENT_NAME)

INSTALLED_APPS = (
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    # Third party apps
    "rest_framework",  # utilities for rest apis
    "rest_framework_simplejwt",  # JWT authentication
    "django_filters",  # for filtering rest endpoints
    "health_check",
    "health_check.db",
    "health_check.contrib.migrations",
    "drf_spectacular",
    # Your apps
    "authentication.users.apps.UsersConfig",
    "authentication.config.apps.ConfigConfig",
)

# Development APPs
if ENVIRONMENT == LOCAL_ENVIRONMENT_NAME:
    INSTALLED_APPS += ("behave_django",)

# https://docs.djangoproject.com/en/2.0/topics/http/middleware/
MIDDLEWARE = (
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
)

ALLOWED_HOSTS = ["*"]
APPLICATION_PORT = env.int("APPLICATION_PORT", 80)
GUNICORN_WORKERS = env.int("GUNICORN_WORKERS", 3)
ROOT_URLCONF = "authentication.urls"
SECRET_KEY = env.str("DJANGO_SECRET_KEY")
WSGI_APPLICATION = "authentication.wsgi.application"

# Email
EMAIL_BACKEND = "django.core.mail.backends.smtp.EmailBackend"

ADMINS = (("Author", "mathias.lantean@sibelhealth.com"),)

# Postgres
DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.postgresql",
        "ATOMIC_REQUESTS": False,
        "NAME": env.str("DB_NAME"),
        "USER": env.str("DB_USERNAME"),
        "PASSWORD": env.str("DB_PASSWORD"),
        "HOST": env.str("DB_HOST"),
        "PORT": env.str("DB_PORT"),
    }
}
# General
APPEND_SLASH = False
TIME_ZONE = "UTC"
LANGUAGE_CODE = "en-us"
DEFAULT_AUTO_FIELD = "django.db.models.AutoField"
# If you set this to False, Django will make some optimizations so as not
# to load the internationalization machinery.
USE_I18N = False
USE_TZ = True
LOGIN_REDIRECT_URL = "/"

# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/2.0/howto/static-files/
STATIC_ROOT = os.path.normpath(join(os.path.dirname(BASE_DIR), "static"))
STATICFILES_DIRS = []
STATIC_URL = "/static/"
STATICFILES_FINDERS = (
    "django.contrib.staticfiles.finders.FileSystemFinder",
    "django.contrib.staticfiles.finders.AppDirectoriesFinder",
)

# Media files
MEDIA_ROOT = join(os.path.dirname(BASE_DIR), "media")
MEDIA_URL = "/media/"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": STATICFILES_DIRS,
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ],
        },
    },
]

# Set DEBUG to False as a default for safety
# https://docs.djangoproject.com/en/dev/ref/settings/#debug
DEBUG = env.bool("DJANGO_DEBUG", False)

# Password Validation
# https://docs.djangoproject.com/en/2.0/topics/auth/passwords/#module-django.contrib.auth.password_validation
AUTH_PASSWORD_VALIDATORS = [
    {
        "NAME": "django.contrib.auth.password_validation.MinimumLengthValidator",
        "OPTIONS": {
            "min_length": 4,
        },
    },
]

# Logging
LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "django.server": {
            "()": "django.utils.log.ServerFormatter",
            "format": "[%(server_time)s] %(message)s",
        },
        "verbose": {
            "format": "%(levelname)s %(asctime)s %(module)s %(process)d %(thread)d %(message)s"
        },
        "simple": {"format": "%(levelname)s %(message)s"},
    },
    "filters": {
        "require_debug_true": {
            "()": "django.utils.log.RequireDebugTrue",
        },
    },
    "handlers": {
        "django.server": {
            "level": "INFO",
            "class": "logging.StreamHandler",
            "formatter": "django.server",
        },
        "console": {
            "level": "DEBUG",
            "class": "logging.StreamHandler",
            "formatter": "simple",
        },
        "mail_admins": {
            "level": "ERROR",
            "class": "django.utils.log.AdminEmailHandler",
        },
    },
    "loggers": {
        "django": {
            "handlers": ["console"],
            "propagate": True,
        },
        "django.server": {
            "handlers": ["django.server"],
            "level": "INFO",
            "propagate": False,
        },
        "django.request": {
            "handlers": ["mail_admins", "console"],
            "level": "ERROR",
            "propagate": False,
        },
        "django.db.backends": {"handlers": ["console"], "level": "INFO"},
    },
}

# Sentry
sentry_sdk.init(
    dsn=env.str("SENTRY_DSN", None),
    traces_sample_rate=env.float("SENTRY_TRACES_SAMPLE_RATE", 0),
    profiles_sample_rate=env.float("SENTRY_PROFILES_SAMPLE_RATE", 0),
    environment=ENVIRONMENT,
    release=env.str("SIBEL_VERSION"),
    send_default_pii=True,
    integrations=[
        DjangoIntegration(),
    ],
)

# Custom user app
AUTH_USER_MODEL = "users.User"
DEFAULT_ADMIN_USERNAME = env.str("DJANGO_SUPERUSER_USERNAME")

ADMIN_PRIVILEGE_NAME = "admin"
CLINICAL_PRIVILEGE_NAME = "clinical"
TECH_PRIVILEGE_NAME = "tech"
ORGANIZATION_PRIVILEGE_NAME = "organization"

ADMIN_PRIVILEGES = [
    ADMIN_PRIVILEGE_NAME,
    CLINICAL_PRIVILEGE_NAME,
    TECH_PRIVILEGE_NAME,
    ORGANIZATION_PRIVILEGE_NAME,
    # Add more if needed
]

# Django Rest Framework
REST_FRAMEWORK = {
    "DEFAULT_PAGINATION_CLASS": "authentication.users.pagination.PageNumberResourcesPagination",
    "PAGE_SIZE": env.int("DJANGO_PAGINATION_LIMIT", 10),
    "DATETIME_FORMAT": "%Y-%m-%dT%H:%M:%S%z",
    "DEFAULT_RENDERER_CLASSES": (
        "rest_framework.renderers.JSONRenderer",
        "rest_framework.renderers.BrowsableAPIRenderer",
    ),
    "DEFAULT_PERMISSION_CLASSES": [
        "rest_framework.permissions.IsAuthenticated",
    ],
    "DEFAULT_AUTHENTICATION_CLASSES": (
        "rest_framework.authentication.SessionAuthentication",
        "rest_framework_simplejwt.authentication.JWTAuthentication",
    ),
    "DEFAULT_SCHEMA_CLASS": "drf_spectacular.openapi.AutoSchema",
}

SPECTACULAR_SETTINGS = {
    "TITLE": "Authentication",
    "DESCRIPTION": (
        "The purpose of this service is to provide secure and"
        " easy-to-use authentication for any web or mobile application."
    ),
    "VERSION": "1.0.0",
    "SERVE_INCLUDE_SCHEMA": False,
}

ACCESS_TOKEN_LIFETIME_IN_MINUTES = env.int("ACCESS_TOKEN_LIFETIME_IN_MINUTES", 15)
REFRESH_TOKEN_LIFETIME_IN_DAYS = env.int("REFRESH_TOKEN_LIFETIME_IN_DAYS", 7)
AUTHENTICATION_FAILURE_THRESHOLD = env.int("AUTHENTICATION_FAILURE_THRESHOLD", 5)
AUTHENTICATION_ACCOUNT_LOCKOUT_IN_MINUTES = env.int("AUTHENTICATION_ACCOUNT_LOCKOUT_IN_MINUTES", 15)

SIMPLE_JWT = {
    "ACCESS_TOKEN_LIFETIME": timedelta(minutes=ACCESS_TOKEN_LIFETIME_IN_MINUTES),
    "REFRESH_TOKEN_LIFETIME": timedelta(days=REFRESH_TOKEN_LIFETIME_IN_DAYS),
    "ALGORITHM": "RS256",
    "AUDIENCE": "tucana",
    "SIGNING_KEY": base64.b64decode(env.str("SECRET_RS256_KEY")).decode("utf-8"),
    "VERIFYING_KEY": base64.b64decode(env.str("PUBLIC_RS256_KEY")).decode("utf-8"),
    "TOKEN_OBTAIN_SERIALIZER": "authentication.users.serializers.TokenObtainPairDetailSerializer",
    "USER_AUTHENTICATION_RULE": "authentication.users.auth.user_authentication_rule_signal",
}

# Kafka settings
KAFKA = {
    "HOST": env.str("KAFKA_HOST"),
    "PORT": env.int("KAFKA_PORT"),
    "TOPICS": {
        "AUDIT": env.str("PUBLISHER_AUDIT_TRAIL_STREAM_NAME"),
    },
    "HANDLER_CLASS": env.str(
        "KAFKA_HANDLER_CLASS", "authentication.broker.publisher_kafka.KafkaPublisher"
    ),
    "KAFKA_CA_FILE_PATH": env.str("KAFKA_CA_FILE_PATH"),
    "KAFKA_CERT_FILE_PATH": env.str("KAFKA_CERT_FILE_PATH"),
    "KAFKA_KEY_FILE_PATH": env.str("KAFKA_KEY_FILE_PATH"),
    "KAFKA_PASSWORD": env.str("KAFKA_PASSWORD"),
}

# Redis settings
PROJECT_NAME = env.str("PROJECT_NAME", "authentication")
BRUTE_FORCE_PROTECTION_ENABLED = env.bool("BRUTE_FORCE_PROTECTION_ENABLED", True)
BRUTE_FORCE_ATTEMPT_TTL = env.int("BRUTE_FORCE_ATTEMPT_TTL")

REDIS = {
    "HOST": env.str("REDIS_HOST"),
    "PORT": env.int("REDIS_PORT"),
    "USERNAME": env.str("REDIS_USERNAME"),
    "PASSWORD": env.str("REDIS_PASSWORD"),
}
