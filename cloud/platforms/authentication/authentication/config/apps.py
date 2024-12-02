from django.apps import AppConfig


class ConfigConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "authentication.config"

    def ready(self):
        # Implicitly connect signal handlers decorated with @receiver.
        from authentication.config import (  # pylint: disable=W0611, C0415  # noqa: F401
            signals,
        )
