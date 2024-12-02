from django.conf import settings
from django.db.models.signals import post_save
from rest_framework import mixins, permissions, status, viewsets
from rest_framework.response import Response

from authentication.cache.redis_cache import (
    delete_app_settings,
    get_app_settings,
    save_app_settings,
)
from authentication.config.models import AppSetting
from authentication.config.serializers import AppSettingBatchCreateSerializer, AppSettingSerializer
from authentication.users.permissions import HasAnyPrivilege


class AppSettingViewSet(
    mixins.CreateModelMixin,
    mixins.ListModelMixin,
    viewsets.GenericViewSet,
):
    queryset = AppSetting.objects.all()
    serializer_class = AppSettingSerializer
    permission_classes = (permissions.IsAdminUser | HasAnyPrivilege,)
    required_privileges = (settings.TECH_PRIVILEGE_NAME,)

    def perform_create(self, serializer):
        app_settings = serializer.validated_data.get("configs")
        for app_setting in app_settings:
            key = app_setting.get("key")
            value = app_setting.get("value")
            obj, created = AppSetting.objects.update_or_create(
                key=key,
                defaults={"value": value},
            )
            post_save.send(sender=AppSetting, instance=obj, created=created, request=self.request)

            # Remove app setting from the cache
            delete_app_settings()

    def create(self, request, *args, **kwargs):
        serializer = AppSettingBatchCreateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)
        return Response(status=status.HTTP_204_NO_CONTENT, headers=headers)

    def list(self, request, *args, **kwargs):
        if cached_app_settings := get_app_settings():
            queryset = cached_app_settings
        else:
            queryset = self.filter_queryset(self.get_queryset())
            # Add app settings to the cache
            save_app_settings(queryset)

        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)
