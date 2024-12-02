from rest_framework import permissions


class IsUserOrReadOnly(permissions.BasePermission):
    """
    Object-level permission to only allow owners of an object to edit it.
    """

    def has_object_permission(self, request, view, obj):
        return obj == request.user


class HasAnyPrivilege(permissions.BasePermission):
    """
    View-level permission to only allow users with one of the given privileges.
    """

    def has_permission(self, request, view):
        allowed = False

        if request.user.is_authenticated:
            required_privileges = getattr(view, "required_privileges", [])
            user_privileges = request.user.privileges.values_list("name", flat=True)

            allowed = any(privilege in user_privileges for privilege in required_privileges)

        return allowed
