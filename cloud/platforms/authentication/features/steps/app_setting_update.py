from unittest.mock import call

from authentication.config.models import AppSetting
from authentication.config.signals import APP_SETTING_ADDED, APP_SETTING_UPDATED
from behave import *
from django.urls import reverse

from features.factories.app_setting_factories import AppSettingFactory


@step("an app setting '{app_setting_name}':'{app_setting_value}' exists")
def step_impl(context, app_setting_name, app_setting_value):
    context.app_setting_name = app_setting_name
    context.app_setting_value = app_setting_value
    context.app_setting = AppSettingFactory(
        key=context.app_setting_name, value=context.app_setting_value
    )


@step("a request to add a set of app settings")
def step_impl(context):
    context.app_settings = {
        "port": "9000",
        "host": "www.example.com",
        "username": "admin",
    }
    configs = [{"key": key, "value": value} for key, value in context.app_settings.items()]
    context.request = {"configs": configs}


@step("a request to add the app setting '{app_setting_name}' : '{new_app_setting_value}'")
@step("a request to update the app setting '{app_setting_name}' to '{new_app_setting_value}'")
def step_impl(context, app_setting_name, new_app_setting_value):
    context.new_app_setting_value = new_app_setting_value
    context.request = {
        "configs": [
            {
                "key": app_setting_name,
                "value": new_app_setting_value,
            }
        ]
    }


@when("the logged in user creates the app setting")
@when("the logged in user creates the app settings")
@when("the logged in user updates the app setting")
def step_impl(context):
    config_list_url = reverse("configuration-list")
    access_token = context.user_session.access
    context.response = context.test.client.post(
        config_list_url,
        context.request,
        content_type="application/json",
        headers={"Authorization": f"Bearer {access_token}"},
    )


@step("the app settings are created")
def step_impl(context):
    for key, value in context.app_settings.items():
        created_app_setting = AppSetting.objects.get(key=key)
        assert created_app_setting.value == value


@step("the app setting '{app_setting_name}' is created")
@step("the app setting '{app_setting_name}' is updated")
def step_impl(context, app_setting_name):
    context.app_setting_name = app_setting_name
    app_setting = AppSetting.objects.get(key=app_setting_name)
    assert app_setting.value == context.new_app_setting_value


@step("the app setting '{app_setting_name}' is not created")
def step_impl(context, app_setting_name):
    context.app_setting_name = app_setting_name
    app_setting = AppSetting.objects.filter(key=app_setting_name)
    assert not app_setting


@step("the app setting create event is logged")
def step_impl(context):
    app_setting = AppSetting.objects.get(key=context.app_setting_name)
    context.publisher_mock.notify.assert_called_with(
        str(app_setting.id), APP_SETTING_ADDED, context.user.id
    )


@step("the app setting update event is logged")
def step_impl(context):
    context.publisher_mock.notify.assert_called_with(
        str(context.app_setting.id), APP_SETTING_UPDATED, context.user.id
    )


@step("the app setting create events are logged")
def step_impl(context):
    calls = []
    for key, value in context.app_settings.items():
        created_app_setting = AppSetting.objects.get(key=key)
        calls.append(call(str(created_app_setting.id), APP_SETTING_ADDED, context.user.id))

    context.publisher_mock.notify.assert_has_calls(calls, any_order=True)
