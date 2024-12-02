import uuid

from behave import step, when
from sqlalchemy import insert, select

from app.common.models import BedGroup
from app.settings import config
from features.environment import AnyDateTime, AnyUUID
from features.steps.common import assert_message_was_published


@step("request to create a bed group")
def step_impl(context):
    context.bed_group = {"id": str(uuid.uuid4()), "name": "Bed Group 1"}
    context.request = {
        "url": "/patient/bed-group/CreateBedGroup",
        "json": context.bed_group,
    }


@when("the request to create a bed group is made")
def step_impl(context):
    context.response = context.client.post(**context.request)


@step("the requested bed group is created")
def step_impl(context):
    stmt = select(BedGroup)
    found_bed_groups = context.db.execute(stmt).scalars().all()
    found_bed_groups_by_id = {str(bed.id): bed for bed in found_bed_groups}
    bed_group_id = context.bed_group["id"]
    assert bed_group_id in found_bed_groups_by_id
    found_bed = found_bed_groups_by_id[bed_group_id]
    assert found_bed.name == context.bed_group["name"]


@step("the creation of the bed group is published")
def step_impl(context):
    topic = config.PATIENT_PUBLISHER_AUDIT_TRAIL_STREAM_NAME
    value = {
        "entity_id": context.bed_group["id"],
        "event_name": "Bed group created",
        "performed_on": AnyDateTime(),
        "performed_by": "b4f6f4e0-6ca5-4be9-99d4-28d66bd82ecd",
        "event_state": {
            "id": context.bed_group["id"],
            "name": context.bed_group["name"],
            "description": context.bed_group.get("description"),
            "beds": [],
        },
        "previous_state": {},
        "entity_name": "patient",
        "emitted_by": "patient",
        "event_type": "BED_GROUP_CREATED_EVENT",
        "message_id": AnyUUID(),
        "event_data": {
            "id": context.bed_group["id"],
            "name": context.bed_group["name"],
            "description": context.bed_group.get("description"),
            "beds": [],
        },
    }
    headers = [("event_type", b"BED_GROUP_CREATED_EVENT")]
    assert_message_was_published(context, topic, value, headers)


@step("the created bed group is returned")
def step_impl(context):
    result = context.response.json()
    assert result
    assert context.bed_group["id"] == result["id"]
    assert context.bed_group["name"] == result["name"]


@step("the requested bed group is not created")
def step_impl(context):
    assert not context.db.get(BedGroup, context.bed_group["id"])


@step("the creation of the bed group is not published")
def step_impl(context):
    context.producer.send_and_wait.assert_not_called()


@step("there is a group with the same name for creation")
def step_impl(context):
    context.db.execute(
        insert(BedGroup),
        [
            {
                "id": "7fc17260-8dcc-4bce-b07b-5dfdf6f409b1",
                "name": context.bed_group["name"],
            }
        ],
    )
    context.db.commit()


@step("the request includes no create a bed group `{field_name}` field")
def step_impl(context, field_name):
    context.request["json"].pop(field_name)
