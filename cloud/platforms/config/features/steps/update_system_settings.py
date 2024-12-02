from behave import *
from sqlalchemy import select

from app.config.models import SystemSettings


@step("a valid request to update the system settings")
def step_impl(context):
    context.request = {"url": "/config/UpdateSystemSettings"}
    request_data = {}
    for row in context.table:
        request_data[row["setting_name"]] = row["setting_value"]
    context.request["json"] = request_data


@when("the request to update system settings is made")
def step_impl(context):
    context.response = context.client.post(**context.request)


@then("the system settings are updated")
def step_impl(context):
    stmt = select(SystemSettings)
    result: SystemSettings = context.db.execute(stmt).scalars().one()
    if "patient_vitals_retention_period_ms" in context.request["json"]:
        assert result.patient_vitals_retention_period_ms == int(
            context.request["json"]["patient_vitals_retention_period_ms"]
        )
