from behave import step

from app.device.src.common.models import Device


@step("a request is made to delete a device")
def step_impl(context):
    context.device_id = "91e6c14f-1142-49c8-9898-971b726b9684"
    context.device_name = "device"
    context.device_primary_identifier = "primary-identifier"
    context.model_number = "145100"
    context.request = {
        "url": "/device/DeleteDevice",
        "json": {
            "device_id": context.device_id,
        },
    }


@step("the request is made to delete the device")
def step_impl(context):
    context.response = context.client.post(**context.request)
    context.db.expire_all()


@step("the device no longer exists")
def step_impl(context):
    device = context.db.get(Device, context.device_id)
    assert not device
