import uuid

from behave import step, when
from sqlalchemy import insert, select

from app.common.models import BedGroup
from app.settings import config
from features.environment import AnyDateTime, AnyUUID
from features.steps.common import assert_message_was_published


@step("request to batch create bed groups")
@step("request to batch create `{number:d}` bed groups")
def step_impl(context, number: int = 2):
    context.bed_groups = [
        {"id": str(uuid.uuid4()), "name": f"Bed Group {i}"} for i in range(number)
    ]
    context.request = {
        "url": "/patient/bed-group/BatchCreateBedGroups",
        "json": {"groups": context.bed_groups},
    }


@when("the request to batch create bed groups is made")
def step_impl(context):
    context.response = context.client.post(**context.request)


@step("the requested bed groups are created")
def step_impl(context):
    stmt = select(BedGroup)
    found_bed_groups = context.db.execute(stmt).scalars().all()
    found_bed_groups_by_id = {str(bed.id): bed for bed in found_bed_groups}
    assert len(found_bed_groups) == len(context.bed_groups)
    for bed_group in context.bed_groups:
        bed_group_id = bed_group["id"]
        assert bed_group_id in found_bed_groups_by_id
        found_bed = found_bed_groups_by_id[bed_group_id]
        assert found_bed.name == bed_group["name"]


@step("the creation of the bed groups is published")
def step_impl(context):
    for group in context.bed_groups:
        topic = config.PATIENT_PUBLISHER_AUDIT_TRAIL_STREAM_NAME
        value = {
            "entity_id": group["id"],
            "event_name": "Bed group created",
            "performed_on": AnyDateTime(),
            "performed_by": "b4f6f4e0-6ca5-4be9-99d4-28d66bd82ecd",
            "event_state": {
                "id": group["id"],
                "name": group["name"],
                "description": group.get("description"),
                "beds": [],
            },
            "previous_state": {},
            "entity_name": "patient",
            "emitted_by": "patient",
            "event_type": "BED_GROUP_CREATED_EVENT",
            "message_id": AnyUUID(),
            "event_data": {
                "id": group["id"],
                "name": group["name"],
                "description": None,
                "beds": [],
            },
        }
        headers = [("event_type", b"BED_GROUP_CREATED_EVENT")]
        assert_message_was_published(context, topic, value, headers)


@step("the created bed groups are returned")
def step_impl(context):
    result = context.response.json()["resources"]
    assert len(result) == len(context.bed_groups)

    found_bed_groups_by_id = {bg["id"]: bg for bg in result}
    for bed_group in context.bed_groups:
        bed_group_id = bed_group["id"]
        assert bed_group_id in found_bed_groups_by_id
        found_bed = found_bed_groups_by_id[bed_group_id]
        assert found_bed["name"] == bed_group["name"]


@step("the requested bed groups are not created")
def step_impl(context):
    ids = [bg["id"] for bg in context.bed_groups]
    assert not context.db.execute(select(BedGroup).where(BedGroup.id.in_(ids))).all()


@step("the creation of the bed groups is not published")
def step_impl(context):
    context.producer.send_and_wait.assert_not_called()


@step("there is a group with the same name")
def step_impl(context):
    context.db.execute(
        insert(BedGroup),
        [
            {
                "id": "7fc17260-8dcc-4bce-b07b-5dfdf6f409b1",
                "name": context.bed_groups[0]["name"],
            }
        ],
    )
    context.db.commit()


@step("the request includes no batch create bed groups `{field_name}` field")
def step_impl(context, field_name):
    if field_name == "groups":
        context.request["json"].pop("groups")
    else:
        context.bed_groups[0].pop(field_name)
