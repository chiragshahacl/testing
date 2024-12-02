import uuid

from behave import step, when
from sqlalchemy import insert, select

from app.common.models import Bed
from app.settings import config
from features.environment import AnyUUID
from features.steps.common import assert_message_was_published


@step("a request to create a bed")
def step_impl(context):
    context.bed = {"id": str(uuid.uuid4()), "name": "Bed XX"}
    context.request = {
        "url": "/patient/bed/CreateBed",
        "json": context.bed,
    }


@when("the request to create a bed is made")
def step_impl(context):
    context.response = context.client.post(**context.request)


@step("the requested bed is created")
def step_impl(context):
    stmt = select(Bed)
    found_beds = context.db.execute(stmt).scalars().all()
    found_beds_by_id = {str(bed.id): bed for bed in found_beds}
    bed_id = context.bed["id"]
    assert bed_id in found_beds_by_id
    found_bed = found_beds_by_id[bed_id]
    assert found_bed.name == context.bed["name"]


@step("64 beds exist")
def step_impl(context, number: int = 64):
    context.db.execute(
        insert(Bed),
        [{"id": str(uuid.uuid4()), "name": f"Bed {i}"} for i in range(number)],
    )
    context.db.commit()


@step("the creation of the bed is published")
def step_impl(context):
    topic = config.PATIENT_PUBLISHER_AUDIT_TRAIL_STREAM_NAME
    value = {
        "entity_id": context.bed["id"],
        "event_name": "Bed created",
        "performed_on": context.now.isoformat(),
        "performed_by": "b4f6f4e0-6ca5-4be9-99d4-28d66bd82ecd",
        "event_state": {
            "id": context.bed["id"],
            "name": context.bed["name"],
        },
        "previous_state": {},
        "entity_name": "patient",
        "emitted_by": "patient",
        "event_type": "BED_CREATED_EVENT",
        "message_id": AnyUUID(),
        "event_data": {
            "id": context.bed["id"],
            "name": context.bed["name"],
        },
    }
    headers = [("event_type", b"BED_CREATED_EVENT")]
    assert_message_was_published(context, topic, value, headers)


@step("the created bed is returned")
def step_impl(context):
    result = context.response.json()
    assert result
    assert context.bed["id"] == result["id"]
    assert context.bed["name"] == result["name"]


@step("the requested bed is not created")
def step_impl(context):
    assert not context.db.execute(select(Bed).where(Bed.id == context.bed["id"])).all()


@step("the creation of the bed is not published")
def step_impl(context):
    context.producer.send_and_wait.assert_not_called()


@step("there is a bed with the same name for creation")
def step_impl(context):
    context.db.execute(
        insert(Bed),
        [
            {
                "id": "3c52ff09-aa6d-4f0e-b605-7b740f0a3a16",
                "name": context.bed["name"],
            }
        ],
    )
    context.db.commit()


@step("the request includes no create bed `{field_name}` field")
def step_impl(context, field_name):
    context.request["json"].pop(field_name)
