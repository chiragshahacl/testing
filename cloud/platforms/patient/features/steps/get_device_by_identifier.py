import datetime

from behave import step

from app.device.src.common.models import Device
from features.steps.device_common import create_alarms_and_vitals


@step("the patient monitor exists")
def step_impl(context):
    device = Device(
        id=context.device_id,
        primary_identifier=context.device_primary_identifier,
        name=context.device_name,
        created_at=datetime.datetime.now(),
        updated_at=datetime.datetime.now(),
        audio_pause_enabled=False,
        audio_enabled=True,
        gateway_id=context.device_id,
    )
    context.db.add(device)
    context.db.flush()
    create_alarms_and_vitals(device, context.db)

    context.db.commit()


@step("a valid request to get a device by identifier")
def step_impl(context):
    context.device_id = "91e6c14f-1142-49c8-9898-971b726b9684"
    context.device_primary_identifier = "primary-identifier"
    context.device_name = "device"
    context.request = {
        "url": f"/device/{context.device_primary_identifier}",
    }


@step("the device identifier id was provided in uppercase")
def step_impl(context):
    context.request["url"] = f"/device/{context.device_primary_identifier.upper()}"


@step("the request is made to get a device by identifier")
def step_impl(context):
    context.response = context.client.get(**context.request)


@step("the device is fetched")
def step_impl(context):
    device = context.db.get(Device, context.device_id)
    assert device
    assert str(device.id) == context.device_id
    assert device.primary_identifier == context.device_primary_identifier
    assert device.name == context.device_name
    assert device.alerts
    assert device.audio_enabled is True
    assert device.audio_pause_enabled is False
