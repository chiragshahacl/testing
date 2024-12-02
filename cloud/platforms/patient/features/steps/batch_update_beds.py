import uuid
from uuid import UUID

from behave import step, when
from sqlalchemy import select

from app.common.models import Bed
from app.settings import config
from features.environment import AnyDateTime, AnyUUID
from features.steps.common import assert_message_was_published


@step("a request to batch update beds")
@step("a request to batch update `{number:d}` beds")
def step_impl(context, number: int = 2):
    context.beds = [
        {"id": str(uuid.uuid4()), "name": f"Updated Bed {i + 1}"} for i in range(number)
    ]
    context.request = {
        "url": "/patient/bed/BatchUpdateBeds",
        "json": {"beds": context.beds},
    }


@when("the request to batch update beds is made")
def step_impl(context):
    context.response = context.client.post(**context.request)
    context.db.expire_all()


@step("the requested beds are updated")
def step_impl(context):
    found_beds = context.db.execute(select(Bed)).scalars().all()
    found_beds_by_id = {str(b.id): b for b in found_beds}
    expected_beds = context.beds
    assert len(expected_beds) == len(found_beds)
    for bed in expected_beds:
        bed_id = bed["id"]
        assert bed_id in found_beds_by_id
        found_bed = found_beds_by_id[bed_id]
        assert found_bed.name == bed["name"], f"{found_bed.name} != {bed['name']}"


@step("the beds to be updated exist")
def step_impl(context):
    beds = context.beds
    for index, bed in enumerate(beds):
        context.db.add(
            Bed(
                id=UUID(bed["id"]),
                name=f"Bed {index}",
            )
        )
    context.db.commit()


@step("the update of the beds is published")
def step_impl(context):
    for index, bed in enumerate(context.beds):
        topic = config.PATIENT_PUBLISHER_AUDIT_TRAIL_STREAM_NAME
        value = {
            "entity_id": bed["id"],
            "event_name": "Bed updated",
            "performed_on": AnyDateTime(),
            "performed_by": "b4f6f4e0-6ca5-4be9-99d4-28d66bd82ecd",
            "event_state": {
                "id": bed["id"],
                "name": bed["name"],
            },
            "previous_state": {
                "id": bed["id"],
                "name": f"Bed {index}",
            },
            "entity_name": "patient",
            "emitted_by": "patient",
            "event_type": "BED_UPDATED_EVENT",
            "message_id": AnyUUID(),
            "event_data": {"name": bed["name"]},
        }
        headers = [("event_type", b"BED_UPDATED_EVENT")]

        assert_message_was_published(context, topic, value, headers)


@step("the updated beds are returned")
def step_impl(context):
    found_beds = context.response.json()["resources"]
    found_beds_by_id = {b["id"]: b for b in found_beds}
    expected_beds = context.beds
    assert len(expected_beds) == len(found_beds)
    for bed in expected_beds:
        bed_id = bed["id"]
        assert bed_id in found_beds_by_id
        found_bed = found_beds_by_id[bed_id]
        assert found_bed["name"] == bed["name"]


@step("the bed number `{number:d}` exist")
def step_impl(context, number: int):
    bed = Bed(
        id=UUID(context.request["json"]["beds"][number]["id"]),
        name=f"Bed {number}",
    )
    context.db.add(bed)
    context.db.commit()


@step("the requested beds are not updated")
def step_impl(context):
    found_beds = context.db.execute(select(Bed)).scalars().all()
    found_beds_by_id = {str(b.id): b for b in found_beds}
    for bed in context.beds:
        if bed["id"] in found_beds_by_id:
            bed_name = found_beds_by_id[bed["id"]].name
            assert bed["name"] != bed_name


@step("the update of the beds is not published")
def step_impl(context):
    context.producer.send_and_wait.assert_not_called()


@step("one of the provided names is already in use by another bed")
def step_impl(context):
    bed = Bed(
        id=uuid.uuid4(),
        name=context.beds[0]["name"],
    )
    context.db.add(bed)
    context.db.commit()
