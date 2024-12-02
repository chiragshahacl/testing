import random
import uuid

from behave import step, when

from app.device.src.common.models import Device, DeviceVitalRange


@step("a request to get a device's vital ranges")
def step_impl(context):
    context.device_id = uuid.UUID("d0b4be29-ad10-4512-a437-4c196cb386ba")
    context.request = {
        "url": f"/device/{context.device_id}/ranges",
    }


@step("the device exists with `{num_ranges:d}` vital ranges")
def step_impl(context, num_ranges: int):
    context.num_ranges = num_ranges
    device = Device(
        id=context.device_id,
        primary_identifier="PID-1",
        name="Device-1",
    )
    context.db.add(device)
    codes = ["10000", "10001", "10002", "10003", "10004"]
    context.vranges = {}
    for i in range(num_ranges):
        vrange = DeviceVitalRange(
            id=uuid.uuid4(),
            code=codes[i],
            upper_limit=random.uniform(100.0, 200.0),
            lower_limit=random.uniform(50.0, 99.9),
            device_id=context.device_id,
        )
        context.vranges.update({str(vrange.id): vrange})
        context.db.add(vrange)

    context.db.commit()


@step("the device exists with `{num_ranges:d}` vital ranges, some out of scope")
def step_impl(context, num_ranges: int):
    context.num_ranges = num_ranges
    device = Device(
        id=context.device_id,
        primary_identifier="PID-1",
        name="Device-1",
    )
    context.db.add(device)
    device2 = Device(
        id=uuid.uuid4(),
        primary_identifier="PID-2",
        name="Device-2",
    )
    context.db.add(device2)
    codes = ["10000", "10001", "10002", "10003", "10004"]
    context.vranges = {}
    for i in range(num_ranges):
        vrange = DeviceVitalRange(
            id=uuid.uuid4(),
            code=codes[i],
            upper_limit=random.uniform(100.0, 200.0),
            lower_limit=random.uniform(50.0, 99.9),
            device_id=context.device_id,
        )
        context.vranges.update({str(vrange.id): vrange})
        context.db.add(vrange)

    for i in range(num_ranges):
        vrange = DeviceVitalRange(
            id=uuid.uuid4(),
            code=codes[i],
            upper_limit=random.uniform(100.0, 200.0),
            lower_limit=random.uniform(50.0, 99.9),
            device_id=device2.id,
        )
        context.db.add(vrange)

    context.db.commit()


@when("the request is made to get a device's vital ranges")
def step_impl(context):
    context.response = context.client.get(**context.request)


@step("the device vital ranges are returned")
def step_impl(context):
    resp = context.response.json()
    assert resp
    for item in resp["resources"]:
        assert item["id"] in context.vranges
        vrange = context.vranges[item["id"]]
        assert vrange.code == item["code"]
        assert vrange.upper_limit == item["upper_limit"]
        assert vrange.lower_limit == item["lower_limit"]
        assert vrange.alert_condition_enabled == item["alert_condition_enabled"]
