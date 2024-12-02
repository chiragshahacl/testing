from django.contrib.auth import get_user_model
from django.contrib.auth.signals import user_logged_out
from django.db.models.signals import post_delete, post_save
from django.shortcuts import get_object_or_404
from rest_framework import generics, mixins, permissions, status, viewsets
from rest_framework.response import Response
from rest_framework.views import APIView

from authentication.users.models import Privilege
from authentication.users.permissions import IsUserOrReadOnly
from authentication.users.schemas import ErrorSchema
from authentication.users.security import (
    authentication_failed_penalization,
    is_authentication_allowed,
)
from authentication.users.serializers import (
    AddMemberSerializer,
    CreateUserSerializer,
    LogoutSerializer,
    PasswordUpdateSerializer,
    PrivilegeSerializer,
    UserSerializer,
)

User = get_user_model()


class Logout(APIView):
    permission_classes = (permissions.IsAuthenticated,)

    def post(self, request):  # pylint: disable=W0613
        """
        Logs out a users.
        """
        serializer = LogoutSerializer(data=request.data, context={"request": request})
        serializer.is_valid(raise_exception=True)

        logged_user = request.user
        if not is_authentication_allowed(logged_user):
            error_body = ErrorSchema(
                loc=["user", "authentication"],
                msg="Account locked.",
                type="account_error.account_locked",
            )
            return Response(status=status.HTTP_403_FORBIDDEN, data=error_body.dict())

        password = serializer.validated_data.get("password")

        if logged_user.is_authenticated and logged_user.check_password(password):
            user_logged_out.send(sender=logged_user.__class__, request=request, user=logged_user)
            return Response(status=status.HTTP_204_NO_CONTENT)

        authentication_failed_penalization(logged_user)

        error_body = ErrorSchema(
            loc=["body", "password"],
            msg="Unable to log out.",
            type="value_error.invalid_password",
        )
        return Response(status=status.HTTP_422_UNPROCESSABLE_ENTITY, data=error_body.dict())


class PasswordUpdateView(generics.CreateAPIView):
    serializer_class = PasswordUpdateSerializer
    permission_classes = (permissions.IsAuthenticated,)

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        if not serializer.is_valid():
            error = serializer.errors.popitem()
            error_body = ErrorSchema(
                loc=["body", error[0]],
                msg=error[1][0],
                type="value_error.invalid_password",
            )
            return Response(status=status.HTTP_422_UNPROCESSABLE_ENTITY, data=error_body.dict())

        user = request.user
        if not is_authentication_allowed(user):
            error_body = ErrorSchema(
                loc=["user", "authentication"],
                msg="Account locked.",
                type="account_error.account_locked",
            )
            return Response(status=status.HTTP_403_FORBIDDEN, data=error_body.dict())

        current_password = serializer.validated_data.get("current_password")
        new_password = serializer.validated_data.get("new_password")

        if not user.check_password(current_password):
            authentication_failed_penalization(user)
            error_body = ErrorSchema(
                loc=["body", "current_password"],
                msg="Wrong password",
                type="value_error.invalid_password",
            )
            return Response(status=status.HTTP_401_UNAUTHORIZED, data=error_body.dict())

        user.set_password(new_password)
        user.save()
        post_save.send(sender=User, instance=user, created=False, request=self.request)

        return Response(status=status.HTTP_204_NO_CONTENT)


class UserViewSet(
    mixins.RetrieveModelMixin,
    mixins.UpdateModelMixin,
    mixins.DestroyModelMixin,
    mixins.ListModelMixin,
    mixins.CreateModelMixin,
    viewsets.GenericViewSet,
):
    """
    Lists, creates, updates and retrieves user accounts
    """

    queryset = User.objects.all()
    serializer_class = UserSerializer

    def get_permissions(self):
        if self.action in ["list", "create"]:
            self.permission_classes = (permissions.IsAdminUser,)
        else:
            self.permission_classes = (IsUserOrReadOnly | permissions.IsAdminUser,)
        return super().get_permissions()

    def get_serializer_class(self):
        user_serializer_class = UserSerializer

        if self.action == "create":
            user_serializer_class = CreateUserSerializer

        return user_serializer_class

    def perform_create(self, serializer):
        user = serializer.save()
        post_save.send(sender=User, instance=user, created=True, request=self.request)

    def perform_update(self, serializer):
        user = serializer.save()
        post_save.send(sender=User, instance=user, created=False, request=self.request)

    def perform_destroy(self, instance):
        instance_id = instance.id
        instance.delete()
        instance.id = instance_id
        post_delete.send(sender=User, instance=instance, request=self.request)


class PrivilegeViewSet(viewsets.ModelViewSet):
    queryset = Privilege.objects.all()
    serializer_class = PrivilegeSerializer
    permission_classes = (permissions.IsAdminUser,)

    def perform_create(self, serializer):
        privilege = serializer.save()
        post_save.send(sender=Privilege, instance=privilege, created=True, request=self.request)

    def perform_update(self, serializer):
        privilege = serializer.save()
        post_save.send(sender=Privilege, instance=privilege, created=False, request=self.request)

    def perform_destroy(self, instance):
        instance_id = instance.id
        instance.delete()
        instance.id = instance_id
        post_delete.send(sender=Privilege, instance=instance, request=self.request)


class MembersViewSet(
    mixins.CreateModelMixin,
    mixins.ListModelMixin,
    mixins.DestroyModelMixin,
    viewsets.GenericViewSet,
):
    queryset = User.objects.none()
    serializer_class = UserSerializer
    permission_classes = (permissions.IsAdminUser,)

    def create(self, request, *args, **kwargs):
        group_pk = kwargs.get("group_pk")
        group = get_object_or_404(Privilege, pk=group_pk)
        serializer = AddMemberSerializer(data=request.data, context={"request": request})
        serializer.is_valid(raise_exception=True)
        user_id = serializer.validated_data.get("user")
        user = get_object_or_404(User, pk=user_id)

        group.request = request
        group.members.add(user)
        return Response(serializer.data)

    def list(self, request, *args, **kwargs):
        group_pk = kwargs.get("group_pk")
        group = get_object_or_404(Privilege, pk=group_pk)
        members = group.members.all()
        page = self.paginate_queryset(members)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = self.get_serializer(members, many=True)
        return Response(serializer.data)

    def destroy(self, request, *args, **kwargs):
        group_pk = kwargs.get("group_pk")
        member_pk = kwargs.get("pk")
        group = get_object_or_404(Privilege, pk=group_pk)
        member = get_object_or_404(group.members, pk=member_pk)

        group.request = request
        group.members.remove(member)
        return Response(status=status.HTTP_204_NO_CONTENT)
