from uuid import UUID

from behave import step, when
from sqlalchemy import select

from app.device.src.common.models import Device, DeviceVitalRange
from app.device.src.device.repository import DEVICE_DEFAULT_VITALS


@step("a request to create a device")
def step_impl(context):
    context.device_id = "91e6c14f-1142-49c8-9898-971b726b9684"
    context.device_name = "device"
    context.device_primary_identifier = "primary-identifier"
    context.model_number = "145100"
    context.request = {
        "url": "/device/CreateDevice",
        "json": {
            "id": context.device_id,
            "name": context.device_name,
            "primary_identifier": context.device_primary_identifier,
            "gateway_id": None,
            "model_number": context.model_number,
            "audio_pause_enabled": False,
            "audio_enabled": True,
        },
    }


@step("a device with the same primary identifier already exists")
def step_impl(context):
    device = Device(
        id="91e6c14f-1142-49c8-9898-971b726b9685",
        primary_identifier=context.device_primary_identifier,
        name="existing device",
        model_number=context.model_number,
    )
    context.db.add(device)
    context.db.commit()


@step("a device with the same id already exists")
def step_impl(context):
    device = Device(
        id=context.device_id,
        primary_identifier="new-primary-identifier",
        name="existing device",
    )
    context.db.add(device)
    context.db.commit()


@step("a device with the gateway id exists")
def step_impl(context):
    device = Device(
        id=UUID(context.request["json"]["gateway_id"]),
        primary_identifier="new-primary-identifier",
        name="existing device",
        model_number=context.model_number,
    )
    context.db.add(device)
    context.db.commit()


@when("the request is made to create a device")
def step_impl(context):
    context.response = context.client.post(**context.request)
    context.db.expire_all()


@step("the device is created")
@step("the device is updated")
def step_impl(context):
    device = context.db.get(Device, context.device_id)
    assert device
    assert str(device.id) == context.device_id
    assert device.name == context.device_name
    assert device.primary_identifier == context.device_primary_identifier
    assert device.model_number == context.model_number
    if getattr(context, "gateway_id", False):
        assert str(device.gateway_id) == context.gateway_id, device.gateway_id


@step("the created device also has default vital ranges")
def step_impl(context):
    stmt = select(DeviceVitalRange).filter(DeviceVitalRange.device_id == context.device_id)
    res = context.db.scalars(stmt).all()
    res_map = {item.code: item for item in res}

    for dvr in DEVICE_DEFAULT_VITALS:
        assert dvr["code"] in res_map
        assert res_map[dvr["code"]].upper_limit == dvr["upper_limit"]
        assert res_map[dvr["code"]].lower_limit == dvr["lower_limit"]


@step("the device is not created")
def step_impl(context):
    device = context.db.get(Device, context.device_id)
    assert not device


@step("the device is assigned a gateway")
def step_impl(context):
    context.gateway_id = "a6019e18-aaf6-44e2-99a0-c0267be058f2"
    context.request["json"]["gateway_id"] = context.gateway_id
