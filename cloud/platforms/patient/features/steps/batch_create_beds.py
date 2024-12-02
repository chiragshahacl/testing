import uuid

from behave import step, when
from sqlalchemy import insert, select

from app.common.models import Bed
from app.settings import config
from features.environment import AnyDateTime, AnyUUID
from features.steps.common import assert_message_was_published


@step("a request to batch create beds")
@step("a request to batch create `{number:d}` beds")
def step_impl(context, number: int = 2):
    context.beds = [{"id": str(uuid.uuid4()), "name": f"Bed {i}"} for i in range(number)]
    context.request = {
        "url": "/patient/bed/BatchCreateBeds",
        "json": {"beds": context.beds},
    }


@when("the request to batch create beds is made")
def step_impl(context):
    context.response = context.client.post(**context.request)


@step("the requested beds are created")
def step_impl(context):
    stmt = select(Bed)
    found_beds = context.db.execute(stmt).scalars().all()
    found_beds_by_id = {str(bed.id): bed for bed in found_beds}
    assert len(found_beds) == len(context.beds)
    for bed in context.beds:
        bed_id = bed["id"]
        assert bed_id in found_beds_by_id
        found_bed = found_beds_by_id[bed_id]
        assert found_bed.name == bed["name"]


@step("one bed exists")
def step_impl(context):
    context.db.execute(
        insert(Bed), [{"id": "43a1e000-cd95-4589-9d3c-805826ae52de", "name": "Bed XX"}]
    )
    context.db.commit()


@step("the creation of the beds is published")
def step_impl(context):
    for bed in context.beds:
        topic = config.PATIENT_PUBLISHER_AUDIT_TRAIL_STREAM_NAME
        value = {
            "entity_id": bed["id"],
            "event_name": "Bed created",
            "performed_on": AnyDateTime(),
            "performed_by": "b4f6f4e0-6ca5-4be9-99d4-28d66bd82ecd",
            "event_state": {
                "id": bed["id"],
                "name": bed["name"],
            },
            "previous_state": {},
            "entity_name": "patient",
            "emitted_by": "patient",
            "event_type": "BED_CREATED_EVENT",
            "message_id": AnyUUID(),
            "event_data": {"id": bed["id"], "name": bed["name"]},
        }
        headers = [("event_type", b"BED_CREATED_EVENT")]
        assert_message_was_published(context, topic, value, headers)


@step("the created beds are returned")
def step_impl(context):
    result = context.response.json()["resources"]
    assert len(result) == len(context.beds)

    found_beds_by_id = {b["id"]: b for b in result}
    for bed in context.beds:
        bed_id = bed["id"]
        assert bed_id in found_beds_by_id
        found_bed = found_beds_by_id[bed_id]
        assert found_bed["name"] == bed["name"]


@step("the requested beds are not created")
def step_impl(context):
    ids = [b["id"] for b in context.beds]
    assert not context.db.execute(select(Bed).where(Bed.id.in_(ids))).all()


@step("the creation of the beds is not published")
def step_impl(context):
    context.producer.send_and_wait.assert_not_called()


@step("there is a bed with the same name")
def step_impl(context):
    context.db.execute(
        insert(Bed),
        [
            {
                "id": "3c52ff09-aa6d-4f0e-b605-7b740f0a3a16",
                "name": context.beds[0]["name"],
            }
        ],
    )
    context.db.commit()


@step("the request includes no batch create bed `{field_name}` field")
def step_impl(context, field_name):
    if field_name == "beds":
        context.request["json"].pop("beds", None)
    else:
        context.beds[0].pop(field_name, None)
