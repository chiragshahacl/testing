from django.contrib.auth.signals import user_logged_in


def user_authentication_rule_signal(user):
    """
    This rule is applied after a valid token is processed.
    """

    is_valid_user = user is not None and user.is_active

    if is_valid_user:
        user_logged_in.send(sender=user.__class__, request=None, user=user)

    return is_valid_user
