import datetime
import uuid

from behave import step, when

from app.device.src.common.models import Device


@step("a request to assign a location to devices")
def step_impl(context):
    context.bed_id = str(uuid.uuid4())
    context.device_id = str(uuid.uuid4())
    context.device_name = "device"
    context.device_primary_identifier = "primary-identifier"

    context.request = {
        "url": "/device/BatchAssignLocation",
        "json": {
            "associations": [
                {
                    "bed_id": context.bed_id,
                    "device_id": context.device_id,
                }
            ],
        },
    }


@step("a request to assign a location to multiple devices")
def step_impl(context):
    context.device_location = {str(uuid.uuid4()): str(uuid.uuid4()) for _ in range(15)}
    context.bed_ids = context.device_location.values()
    associations_list = []
    for device, location in context.device_location.items():
        associations_list.append(
            {
                "bed_id": location,
                "device_id": device,
            }
        )

    context.request = {
        "url": "/device/BatchAssignLocation",
        "json": {"associations": associations_list},
    }


@step("the devices exist")
def step_impl(context):
    for device_id, _ in context.device_location.items():
        device = Device(
            id=device_id,
            primary_identifier=f"test identifier {device_id}",
            name=f"name {device_id}",
            created_at=datetime.datetime.now(),
            updated_at=datetime.datetime.now(),
        )
        context.db.add(device)

        context.db.commit()


@when("the request is made to assign locations")
def step_impl(context):
    context.response = context.client.post(**context.request)
    context.db.expire_all()


@step("the device location is assigned correctly")
def step_impl(context):
    device = context.db.get(Device, context.device_id)
    assert device
    assert str(device.location_id) == context.bed_id


@step("the request payload is wrong")
def step_impl(context):
    context.request["json"] = {"invalid": "invalid"}


@step("the location is already assigned to other device")
def step_impl(context):
    device = Device(
        id=str(uuid.uuid4()),
        primary_identifier="other-identifier",
        location_id=context.bed_id,
        name="other-device",
        created_at=datetime.datetime.now(),
        updated_at=datetime.datetime.now(),
    )
    context.db.add(device)
    context.db.commit()


@step("the device location is not assigned")
def step_impl(context):
    device = context.db.get(Device, context.device_id)
    assert device
    assert device.location_id is None


@step("the devices locations are assigned correctly")
def step_impl(context):
    for device_id, bed_id in context.device_location.items():
        device = context.db.get(Device, device_id)
        assert device
        assert str(device.location_id) == bed_id
