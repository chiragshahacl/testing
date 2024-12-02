import uuid

from django.conf import settings
from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils.translation import gettext_lazy as _


class Privilege(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(_("name"), max_length=150, unique=True)

    objects = models.Manager()

    def __str__(self):
        return str(self.name)

    class Meta:
        ordering = ["name"]
        verbose_name = _("privilege")
        verbose_name_plural = _("privileges")


class User(AbstractUser):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    tenant_id = models.CharField(_("tenant_id"), max_length=100, default="sibel")
    privileges = models.ManyToManyField(
        Privilege,
        verbose_name=_("privileges"),
        blank=True,
        help_text=_(
            "The privileges this user has. Specify rights and "
            "permissions that a particular user has been granted within a system."
        ),
        related_name="members",
        related_query_name="user",
        through="Membership",
        through_fields=("user", "privilege"),
    )
    blocked_until = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return str(self.username)

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)

        if self.is_superuser:
            privilege, _ = Privilege.objects.get_or_create(name=settings.ADMIN_PRIVILEGE_NAME)
            privilege.members.add(self)

    class Meta:
        ordering = ["id"]
        verbose_name = _("user")
        verbose_name_plural = _("users")


class Membership(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    privilege = models.ForeignKey(Privilege, on_delete=models.CASCADE)
