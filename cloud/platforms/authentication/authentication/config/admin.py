from django.contrib import admin

from authentication.config.models import AppSetting


class AppSettingAdmin(admin.ModelAdmin):
    list_display = ["key", "value"]


admin.site.register(AppSetting, AppSettingAdmin)
