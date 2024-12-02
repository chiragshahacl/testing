from common.utils import load_backend
from django.conf import settings
from django.db.models.signals import post_save
from django.dispatch import receiver

from authentication.config.models import AppSetting

Publisher = load_backend(settings.KAFKA.get("HANDLER_CLASS"))

# Event types for User model
APP_SETTING_ADDED = "App setting added"
APP_SETTING_UPDATED = "App setting updated"


@receiver(post_save, sender=AppSetting)
def app_setting_added_or_updated(instance, created, **kwargs):
    request = kwargs.get("request", None)

    if request:
        publisher = Publisher()
        performed_by = str(request.user.id) if request.user else ""
        event_message = APP_SETTING_ADDED if created else APP_SETTING_UPDATED

        publisher.notify(str(instance.id), event_message, performed_by)
