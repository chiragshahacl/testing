from authentication.cache.redis_cache import delete_app_settings
from behave import *
from django.urls import reverse

from features.DTOs.app_setting import AppSettingPaginationDTO
from features.factories.app_setting_factories import AppSettingFactory


@step("app settings exists")
def step_impl(context):
    context.app_setting_batch_size = 15
    context.app_settings = AppSettingFactory.create_batch(context.app_setting_batch_size)


@when("request the list of app settings")
def step_impl(context):
    app_setting_list_url = reverse("configuration-list")
    access_token = context.user_session.access
    context.response = context.test.client.get(
        app_setting_list_url,
        headers={"Authorization": f"Bearer {access_token}"},
    )


@step("the list of app settings is correct")
def step_impl(context):
    app_setting_list = AppSettingPaginationDTO(**context.response.data)
    assert app_setting_list.count == context.app_setting_batch_size


@step("there are not app settings defined")
def step_impl(context):
    delete_app_settings()
    context.app_setting_batch_size = 0
