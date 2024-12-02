import logging

from uvicorn.workers import UvicornWorker

from src.settings import settings


class HealthCheckFilter(logging.Filter):
    def filter(self, record):
        message = record.getMessage()
        # Added condition here because health log shall only be added just for development and qa env only
        if settings.ENVIRONMENT not in ["dev", "qa"]:
            if "GET /health" in message or f"GET {settings.BASE_PATH}/health" in message:
                return False
        return True


LOG_CONFIG = {
    "disable_existing_loggers": False,
    "formatters": {
        "access": {
            "()": "uvicorn.logging.AccessFormatter",
            "fmt": '%(levelprefix)s %(client_addr)s - "%(request_line)s" %(status_code)s',
        },
        "default": {
            "()": "uvicorn.logging.DefaultFormatter",
            "fmt": "%(levelprefix)s %(message)s",
            "use_colors": None,
        },
    },
    "handlers": {
        "access": {
            "class": "logging.StreamHandler",
            "formatter": "access",
            "stream": "ext://sys.stdout",
            "filters": ["health_check_filter"],  # Add your filter here
        },
        "default": {
            "class": "logging.StreamHandler",
            "formatter": "default",
            "stream": "ext://sys.stderr",
        },
    },
    "loggers": {
        "uvicorn": {"handlers": ["default"], "level": "INFO", "propagate": False},
        "uvicorn.access": {"handlers": ["access"], "level": "INFO", "propagate": False},
        "uvicorn.error": {"level": "INFO"},
    },
    "filters": {
        "health_check_filter": {
            "()": HealthCheckFilter,
        },
    },
    "version": 1,
}


class CustomLogWorker(UvicornWorker):
    """Custom worker designed to exclude query parameters from access logs"""

    CONFIG_KWARGS = {
        "loop": "asyncio",
        "http": "h11",
        "lifespan": "on",
        "log_config": LOG_CONFIG,
        "access_log": True,
    }


port = settings.APPLICATION_PORT
bind = f"0.0.0.0:{port}"
workers = settings.GUNICORN_WORKERS
worker_class = "gunicorn_conf.CustomLogWorker"
accesslog = "-"
