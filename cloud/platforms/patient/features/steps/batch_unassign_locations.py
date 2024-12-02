import datetime
import uuid

from behave import step, when

from app.device.src.common.models import Device
from app.settings import config
from features.environment import AnyDateTime, AnyUUID
from features.steps.common import assert_message_was_published


@step("a valid request to batch unassign location from devices")
def step_impl(context):
    context.device_ids = [str(uuid.uuid4()) for _ in range(5)]
    context.bed_ids = [str(uuid.uuid4()) for _ in range(5)]

    context.request = {
        "url": "/device/BatchUnassignLocation",
        "json": {"device_ids": context.device_ids},
    }


@step("the devices in the request exist")
def step_impl(context):
    for index, device_id in enumerate(context.device_ids):
        device = Device(
            id=device_id,
            primary_identifier=f"test identifier {device_id}",
            name=f"name {device_id}",
            created_at=datetime.datetime.now(),
            location_id=context.bed_ids[index],
            updated_at=datetime.datetime.now(),
        )
        context.db.add(device)

        context.db.commit()


@step("one device in the request does not exist")
def step_impl(context):
    for index, device_id in enumerate(context.device_ids[1:]):
        device = Device(
            id=device_id,
            primary_identifier=f"test identifier {device_id}",
            name=f"name {device_id}",
            location_id=context.bed_ids[index],
            created_at=datetime.datetime.now(),
            updated_at=datetime.datetime.now(),
        )
        context.db.add(device)

        context.db.commit()


@step("some other devices with assigned location not in the request exist")
def step_impl(context):
    device_ids = [str(uuid.uuid4()) for _ in range(5)]
    for device_id in device_ids:
        device = Device(
            id=device_id,
            primary_identifier=f"test identifier {device_id}",
            name=f"name {device_id}",
            created_at=datetime.datetime.now(),
            updated_at=datetime.datetime.now(),
        )
        context.db.add(device)

        context.db.commit()


@when("the application receives the request to batch unassign location from devices")
def step_impl(context):
    context.response = context.client.post(**context.request)
    context.db.expire_all()


@step("the location is unassigned from the devices in the request")
def step_impl(context):
    for device_id in context.device_ids:
        device = context.db.get(Device, device_id)
        assert device
        assert device.location_id is None


@step("no location is unassigned")
def step_impl(context):
    for device_id in context.device_ids[1:]:
        device = context.db.get(Device, device_id)
        assert device
        assert device.location_id is not None


@step("the unassigned events are published")
def step_impl(context):
    for index, device_id in enumerate(context.device_ids):
        topic = config.PATIENT_PUBLISHER_AUDIT_TRAIL_STREAM_NAME
        model_number = "sibel"  # This is the default value for device type
        value = {
            "entity_id": device_id,
            "event_name": "Unassign location",
            "performed_on": AnyDateTime(),
            "performed_by": "b4f6f4e0-6ca5-4be9-99d4-28d66bd82ecd",
            "event_state": {
                "id": device_id,
                "primary_identifier": f"test identifier {device_id}",
                "name": f"name {device_id}",
                "model_number": model_number,
                "location_id": None,
                "gateway_id": None,
                "audio_pause_enabled": False,
                "audio_enabled": True,
            },
            "previous_state": {
                "id": device_id,
                "primary_identifier": f"test identifier {device_id}",
                "name": f"name {device_id}",
                "model_number": model_number,
                "location_id": f"{str(context.bed_ids[index])}",
                "gateway_id": None,
                "audio_pause_enabled": False,
                "audio_enabled": True,
            },
            "event_data": {},
            "entity_name": "patient",
            "emitted_by": "patient",
            "event_type": "UNASSIGN_DEVICE_LOCATION_EVENT",
            "message_id": AnyUUID(),
        }
        headers = [("event_type", b"UNASSIGN_DEVICE_LOCATION_EVENT")]
        assert_message_was_published(context, topic, value, headers)


@step("the unassigned events are not published")
def step_impl(context):
    context.producer.send_and_wait.assert_not_called()
