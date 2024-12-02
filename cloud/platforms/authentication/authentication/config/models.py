import uuid

from django.db import models
from django.utils.translation import gettext_lazy as _


class AppSetting(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    key = models.CharField(_("key"), max_length=150, unique=True)
    value = models.CharField(_("value"), max_length=150, blank=False, null=False)

    objects = models.Manager()

    def __str__(self):
        return f"{self.key}: {self.value}"

    class Meta:
        ordering = ["key"]
        verbose_name = _("application setting")
        verbose_name_plural = _("application settings")
