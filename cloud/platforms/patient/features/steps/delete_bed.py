from uuid import UUID

from behave import step, when

from app.common.models import Bed, BedGroup
from app.settings import config
from features.environment import (
    AnyDateTime,
    AnyUUID,
    get_new_db_engine,
    get_new_db_session,
)
from features.steps.common import assert_message_was_published


@step("a request to delete bed by id")
def step_impl(context):
    context.bed_id = "445b234b-ab5a-49e7-a6e8-6b81fe513862"
    context.bed_name = "Bed 1"
    context.bed = Bed(id=UUID(context.bed_id), name=context.bed_name)
    context.group_id = "1ed5bef9-6c89-4acc-acef-eae7fcfdf31d"
    context.request = {
        "url": "/patient/bed/DeleteBed",
        "json": {"bed_id": context.bed_id},
    }


@step("a bed does not exist")
def step_impl(context):
    pass


@step("no group is assigned to the bed")
def step_impl(context):
    context.db.add(context.bed)
    context.db.commit()


@step("a group is assigned to the bed")
def step_impl(context):
    bed_group = BedGroup(
        id=UUID(context.group_id),
        name="Bed Group 1",
    )
    bed_group.beds.append(context.bed)
    context.db.add(bed_group)
    context.db.add(context.bed)
    context.db.commit()


@when("the request is made to delete bed by id")
def step_impl(context):
    context.response = context.client.post(**context.request)


@step("the deleted bed no longer exists")
def step_impl(context):
    engine = get_new_db_engine()
    session = get_new_db_session(engine)
    bed = session.get(Bed, context.bed_id)

    assert not bed

    session.close()


@step("the delete bed event is published")
def step_impl(context):
    topic = config.PATIENT_PUBLISHER_AUDIT_TRAIL_STREAM_NAME
    value = {
        "entity_id": context.bed_id,
        "event_name": "Bed deleted",
        "performed_on": AnyDateTime(),
        "performed_by": "b4f6f4e0-6ca5-4be9-99d4-28d66bd82ecd",
        "event_state": {
            "id": context.bed_id,
            "name": context.bed_name,
        },
        "previous_state": {
            "id": context.bed_id,
            "name": context.bed_name,
        },
        "entity_name": "patient",
        "emitted_by": "patient",
        "event_type": "BED_DELETED_EVENT",
        "message_id": AnyUUID(),
        "event_data": {},
    }
    headers = [("event_type", b"BED_DELETED_EVENT")]
    assert_message_was_published(context, topic, value, headers)


@step("no bed is deleted")
def step_impl(context):
    bed = context.db.get(Bed, context.bed_id)
    assert bed
