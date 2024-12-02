from rest_framework import serializers

from authentication.config.models import AppSetting


class AppSettingSerializer(serializers.ModelSerializer):
    key = serializers.CharField(validators=[])

    class Meta:
        model = AppSetting
        fields = (
            "key",
            "value",
        )


class AppSettingBatchCreateSerializer(serializers.Serializer):
    configs = serializers.ListField(child=AppSettingSerializer())
