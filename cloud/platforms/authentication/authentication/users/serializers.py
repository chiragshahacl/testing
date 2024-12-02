import django.contrib.auth.password_validation as validators
from django.contrib.auth import get_user_model
from django.contrib.auth.validators import UnicodeUsernameValidator
from django.core import exceptions
from rest_framework import exceptions as rest_framework_exceptions
from rest_framework import serializers
from rest_framework.exceptions import PermissionDenied
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer

from authentication.users.models import Privilege
from authentication.users.security import (
    authentication_failed_penalization,
    is_authentication_allowed,
)

User = get_user_model()


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = (
            "id",
            "username",
            "tenant_id",
            "email",
            "first_name",
            "last_name",
        )
        read_only_fields = ("username",)


class CreateUserSerializer(serializers.ModelSerializer):
    def create(self, validated_data):
        # call create_user on user object. Without this
        # the password will be stored in plain text.
        user = User.objects.create_user(**validated_data)
        return user

    class Meta:
        model = User
        fields = (
            "id",
            "username",
            "password",
            "tenant_id",
            "first_name",
            "last_name",
            "email",
        )
        extra_kwargs = {"password": {"write_only": True}}


class ManagementGetOrCreateUserSerializer(serializers.ModelSerializer):
    username_validator = UnicodeUsernameValidator()

    username = serializers.CharField(validators=[username_validator])

    def create(self, validated_data):
        # Creates a user if one does not already exist, or returns the existing user if present.
        # When the user is created, the `create_user` function is called on the User object.
        # This is crucial because without using `create_user`, the password would be stored
        # in plain text. For more information, see:
        # https://stackoverflow.com/questions/10372877/how-to-create-a-user-in-django
        try:
            user = User.objects.get(username=validated_data["username"])
        except User.DoesNotExist:
            user = User.objects.create_user(**validated_data)
        return user

    class Meta:
        model = User
        fields = (
            "id",
            "username",
            "password",
            "tenant_id",
            "first_name",
            "last_name",
            "email",
        )
        extra_kwargs = {"password": {"write_only": True}}


class PrivilegeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Privilege
        fields = (
            "id",
            "name",
        )


class AddMemberSerializer(serializers.Serializer):  # pylint: disable=W0223
    user = serializers.UUIDField()


class TokenObtainPairDetailSerializer(TokenObtainPairSerializer):  # pylint: disable=W0223
    def validate(self, attrs):
        if username := self.initial_data.get(self.username_field):
            try:
                user = User.objects.get(username=username)
                if is_authentication_allowed(user):
                    try:
                        return super().validate(attrs)
                    except rest_framework_exceptions.AuthenticationFailed:
                        authentication_failed_penalization(user)
                else:
                    raise PermissionDenied(detail="Account locked.")
            except User.DoesNotExist:
                pass

        return super().validate(attrs)

    @classmethod
    def get_token(cls, user):
        token = super().get_token(user)

        # Add custom claims
        token["username"] = user.username
        token["tenant_id"] = user.tenant_id
        token["groups"] = list(user.privileges.all().values("name").values_list("name", flat=True))

        return token


class LogoutSerializer(serializers.Serializer):  # pylint: disable=W0223
    password = serializers.CharField(required=True)


class PasswordUpdateSerializer(serializers.Serializer):  # pylint: disable=W0223
    current_password = serializers.CharField(required=True)
    new_password = serializers.CharField(required=True)

    def validate(self, attrs):
        user = self.context.get("request").user
        password = attrs.get("new_password")

        errors = {}
        try:
            validators.validate_password(password=password, user=user)

        except exceptions.ValidationError as error:
            errors["new_password"] = list(error.messages)

        if errors:
            raise serializers.ValidationError(errors)

        return super().validate(attrs)
