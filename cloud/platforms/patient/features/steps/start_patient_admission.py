import uuid

from behave import step, when
from sqlalchemy import select
from test_tools import assert_contains

from app.encounter.enums import EncounterStatus
from app.encounter.events import PlanPatientEncounter
from app.encounter.models import Encounter
from app.settings import config
from features.environment import AnyDateTime, AnyUUID
from features.factories.bed_factories import BedFactory
from features.factories.device_factories import DeviceFactory
from features.factories.encounter import EncounterFactory
from features.factories.patient_factories import PatientFactory
from features.steps.common import assert_message_was_published


@step("a request to plan a patient admission")
def create_encounter(context):
    context.bed = BedFactory.build()
    context.db.add(context.bed)
    context.db.commit()

    context.device = DeviceFactory.build(location_id=context.bed.id)
    context.db.add(context.device)
    context.db.commit()

    context.patient = PatientFactory.build()
    context.db.add(context.patient)
    context.db.commit()

    context.request = {
        "url": "/patient/PlanPatientAdmission",
        "json": {
            "subject_id": context.patient.id,
            "bed_id": context.bed.id,
        },
    }


@when("the request is made to plan a patient admission")
def step_impl(context):
    context.response = context.client.post(**context.request)


@step("the planned encounter is created")
def step_impl(context):
    stmt = select(Encounter).where(Encounter.subject_id == uuid.UUID(context.patient.id))
    context.encounter = context.db.execute(stmt).scalars().one_or_none()

    assert context.encounter
    assert str(context.encounter.subject_id) == context.patient.id
    assert context.encounter.device_id == context.device.id
    assert EncounterStatus.PLANNED.value == context.encounter.status.value


@step("the planned encounter is not created")
def step_impl(context):
    stmt = select(Encounter).where(Encounter.subject_id == uuid.UUID(context.patient.id))
    context.encounter = context.db.execute(stmt).scalars().one_or_none()

    assert not context.encounter


@step("the new planned encounter is returned")
def check_new_patient(context):
    resp = context.response.json()

    assert_contains(
        resp,
        {
            "device_id": str(context.device.id),
            "subject_id": context.patient.id,
            "status": EncounterStatus.PLANNED.value,
            "end_time": context.encounter.end_time,
            "start_time": context.encounter.start_time,
            "created_at": context.encounter.created_at.isoformat(sep="T", timespec="auto"),
        },
    )


@step("the patient encounter planned event is published")
def step_impl(context):
    expected_value = {
        "entity_id": str(context.patient.id),
        "event_name": PlanPatientEncounter.display_name,
        "performed_on": AnyDateTime(),
        "performed_by": "b4f6f4e0-6ca5-4be9-99d4-28d66bd82ecd",
        "event_state": {
            "id": AnyUUID(),
            "status": EncounterStatus.PLANNED.value,
            "created_at": AnyDateTime(),
            "start_time": None,
            "end_time": None,
            "device": context.device.as_dict(),
            "patient": context.patient.as_dict(),
        },
        "previous_state": {},
        "event_type": PlanPatientEncounter.event_type,
        "message_id": AnyUUID(),
        "event_data": {},
        "entity_name": "patient",
        "emitted_by": "patient",
    }

    topic = config.PATIENT_PUBLISHER_AUDIT_TRAIL_STREAM_NAME
    headers = [("event_type", b"PATIENT_ENCOUNTER_PLANNED")]
    assert_message_was_published(context, topic, expected_value, headers)


@step("the bed id is incorrect")
def step_impl(context):
    context.request["json"].update({"bed_id": str(uuid.uuid4())})


@step("the patient id is incorrect")
def step_impl(context):
    context.request["json"].update({"subject_id": str(uuid.uuid4())})


@step("an encounter for the patient and device already exists")
def step_impl(context):
    context.initial_encounter_status = EncounterStatus.PLANNED
    context.previous_encounter = EncounterFactory.build(
        device=context.device,
        subject=context.patient,
        status=context.initial_encounter_status,
    )
    context.db.add(context.previous_encounter)
    context.db.commit()


@step("an encounter for the patient already exists")
def step_impl(context):
    other_bed = BedFactory.build()
    context.db.add(other_bed)
    context.db.commit()

    other_device = DeviceFactory.build(location_id=other_bed.id)
    context.db.add(other_device)
    context.db.commit()

    context.initial_encounter_status = EncounterStatus.PLANNED
    context.previous_encounter = EncounterFactory.build(
        device=other_device,
        subject=context.patient,
        status=context.initial_encounter_status,
    )
    context.db.add(context.previous_encounter)
    context.db.commit()


@step("an encounter for the device already exists")
@step("an encounter for the device already exists with status `{encounter_status}`")
def step_impl(context, encounter_status=EncounterStatus.PLANNED.value):
    other_patient = PatientFactory.build()
    context.db.add(other_patient)
    context.db.commit()

    context.initial_encounter_status = EncounterStatus(encounter_status)
    context.previous_encounter = EncounterFactory.build(
        device=context.device,
        subject=other_patient,
        status=context.initial_encounter_status,
    )
    context.db.add(context.previous_encounter)
    context.db.commit()
