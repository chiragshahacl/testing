from django.apps import AppConfig


class UsersConfig(AppConfig):
    name = "authentication.users"

    def ready(self):
        # Implicitly connect signal handlers decorated with @receiver.
        from authentication.users import (  # pylint: disable=W0611, C0415  # noqa: F401
            signals,
        )
