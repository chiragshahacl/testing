from behave import *
from sqlalchemy import select

from app.config.models import SystemSettings
from app.config.schemas import SystemSettingsSchema


@step("the current system settings are being requested")
def step_impl(context):
    context.request = {"url": "/config/system-settings"}


@when("the users requests the current system settings")
def step_impl(context):
    context.response = context.client.get(**context.request)


@step("the current system settings are returned")
def step_impl(context):
    assert context.response
    assert SystemSettingsSchema.model_validate_json(context.response.content)


@step("system settings exists with values")
def step_impl(context):
    stmt = select(SystemSettings)
    current_settings = context.db.execute(stmt).scalars().one()
    for row in context.table:
        setattr(current_settings, row["setting_name"], row["setting_value"])
    context.db.add(current_settings)
