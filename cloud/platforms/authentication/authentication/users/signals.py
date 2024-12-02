from common.utils import load_backend
from django.conf import settings
from django.contrib.auth import get_user_model
from django.contrib.auth.signals import user_logged_in, user_logged_out
from django.db.models.signals import m2m_changed, post_delete, post_save
from django.dispatch import receiver

from authentication.users.models import Membership, Privilege

User = get_user_model()
Publisher = load_backend(settings.KAFKA.get("HANDLER_CLASS"))

# Event types for User model
USER_ADDED = "User added"
USER_UPDATED = "User updated"
USER_REMOVED = "User removed"

# Event types for user_logged_in and user_logged_out
USER_LOGIN = "Login"
USER_LOGOUT = "Logout"
USER_LOCKED = "Account locked"

# Event types for Privilege model
GROUP_ADDED = "Group added"
GROUP_REMOVED = "Group removed"
GROUP_UPDATED = "Group updated"

# Event type for membership
USER_ADDED_TO_GROUP = "User added to group"
USER_REMOVED_FROM_GROUP = "User removed from group"


@receiver(post_save, sender=User)
def user_added_or_updated(instance, created, **kwargs):
    request = kwargs.get("request", None)

    if request:
        publisher = Publisher()
        performed_by = str(request.user.id) if request.user else ""
        event_message = USER_ADDED if created else USER_UPDATED

        publisher.notify(str(instance.id), event_message, performed_by)


@receiver(post_delete, sender=User)
def user_removed(instance, **kwargs):
    request = kwargs.get("request", None)

    if request:
        publisher = Publisher()
        performed_by = str(request.user.id) if request.user else ""

        publisher.notify(str(instance.id), USER_REMOVED, performed_by)


@receiver(user_logged_in)
def user_log_in(user, **kwargs):  # pylint: disable=W0613
    if user:
        publisher = Publisher()
        publisher.notify(str(user.id), USER_LOGIN, str(user.id))


@receiver(user_logged_out)
def user_log_out(request, user, **kwargs):  # pylint: disable=W0613
    if request and user:
        publisher = Publisher()
        publisher.notify(str(user.id), USER_LOGOUT, str(request.user.id))


@receiver(post_save, sender=Privilege)
def group_added_or_updated(instance, created, **kwargs):
    request = kwargs.get("request", None)

    if request:
        publisher = Publisher()
        performed_by = str(request.user.id) if request.user else ""
        event_message = GROUP_ADDED if created else GROUP_UPDATED

        publisher.notify(str(instance.id), event_message, performed_by)


@receiver(post_delete, sender=Privilege)
def group_removed(instance, **kwargs):  # pylint: disable=W0613
    request = kwargs.get("request", None)

    if request:
        publisher = Publisher()
        performed_by = str(request.user.id) if request.user else ""

        publisher.notify(str(instance.id), GROUP_REMOVED, performed_by)


@receiver(m2m_changed, sender=Membership)
def member_signal_handler(instance, action, **kwargs):  # pylint: disable=W0613
    request = getattr(instance, "request", None)

    if request and action in ["post_add", "post_remove", "post_clear"]:
        performed_by = request.user.id
        group_id = instance.id
        event_message = USER_ADDED_TO_GROUP if action == "post_add" else USER_REMOVED_FROM_GROUP
        publisher = Publisher()

        publisher.notify(str(group_id), event_message, str(performed_by))


def publish_user_account_blocked(user):
    publisher = Publisher()
    publisher.notify(str(user.id), USER_LOCKED, "system")
