from uuid import UUID

from behave import *
from sqlalchemy import select
from starlette import status

from app.encounter.enums import EncounterStatus
from app.encounter.models import Encounter
from app.settings import config
from features.environment import AnyDateTime, AnyUUID
from features.factories.device_factories import DeviceFactory
from features.factories.encounter import EncounterFactory
from features.steps.common import assert_message_was_published


@step("a request is made to dismiss an admission")
def step_impl(context):
    context.patient_id = UUID("4761c2a1-6e59-457d-a48e-25b97333dcf3")
    context.request = {
        "json": {
            "patient_id": str(context.patient_id),
        },
        "url": "/patient/DismissPatientAdmission",
    }


@step("the encounter exists")
@step("the encounter exists with status `{encounter_status}`")
def step_impl(context, encounter_status: str = EncounterStatus.IN_PROGRESS.value):
    status = EncounterStatus(encounter_status)
    context.initial_encounter_status = status
    device = DeviceFactory.build()
    context.db.add(device)
    encounter = EncounterFactory.build(subject=context.patient, device=device, status=status)
    context.db.add(encounter)
    context.db.commit()
    context.device = device
    context.encounter = encounter
    context.db.refresh(encounter)
    context.db.refresh(device)


@when("the request to dismiss an admission is made")
def step_impl(context):
    context.response = context.client.post(**context.request)


@step("the admission doesn't exist any more")
def step_impl(context):
    encounter = context.db.execute(select(Encounter)).scalars().one_or_none()
    assert not encounter, encounter


@step("the admission dismissal is published")
def step_impl(context):
    value = {
        "entity_id": AnyUUID(),
        "event_name": "Patient admission dismissed",
        "performed_on": AnyDateTime(),
        "performed_by": "b4f6f4e0-6ca5-4be9-99d4-28d66bd82ecd",
        "event_state": {
            "id": AnyUUID(),
            "status": "cancelled",
            "created_at": AnyDateTime(),
            "start_time": AnyDateTime(allow_empty=True),
            "end_time": AnyDateTime(allow_empty=True),
            "device": context.device.as_dict(),
            "patient": context.patient.as_dict(),
        },
        "previous_state": {
            "id": AnyUUID(),
            "status": "cancelled",
            "created_at": AnyDateTime(),
            "start_time": AnyDateTime(allow_empty=True),
            "end_time": AnyDateTime(allow_empty=True),
            "device": context.device.as_dict(),
            "patient": context.patient.as_dict(),
        },
        "event_type": "PATIENT_ADMISSION_DISMISSED",
        "message_id": AnyUUID(),
        "event_data": {},
        "entity_name": "patient",
        "emitted_by": "patient",
    }
    headers = [("event_type", b"PATIENT_ADMISSION_DISMISSED")]
    assert_message_was_published(
        context, config.PATIENT_PUBLISHER_AUDIT_TRAIL_STREAM_NAME, value, headers
    )


@then("the user is told the request was rejected")
def step_impl(context):
    assert context.response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
