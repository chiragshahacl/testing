from datetime import timedelta
from uuid import UUID

from behave import step, when

from app.common.models import Patient
from app.patient.enums import GenderEnum
from app.settings import config
from features.environment import (
    AnyDateTime,
    AnyUUID,
    get_new_db_engine,
    get_new_db_session,
)
from features.factories.observation_factories import ObservationFactory
from features.factories.physiological_alert_factory import PhysiologicalAlertFactory
from features.steps.common import assert_message_was_published


@step("a request to delete patient by id")
def step_impl(context):
    context.del_patient_id = "445b234b-ab5a-49e7-a6e8-6b81fe513862"
    context.patient_to_delete = Patient(
        id=UUID(context.del_patient_id),
        primary_identifier="PID-3",
        active=True,
        given_name="PatientD",
        family_name="family",
        gender=GenderEnum.MALE,
        birth_date="2020-03-29",
    )
    context.request = {
        "url": "/patient/DeletePatient",
        "json": {"id": context.del_patient_id},
    }


@step("several patients exist, including patient to be deleted")
def step_impl(context):
    context.patients_by_id = {
        "00e72ed2-159f-48af-8832-56da41d35a0e": Patient(
            id=UUID("00e72ed2-159f-48af-8832-56da41d35a0e"),
            primary_identifier="PID-1",
            active=True,
            given_name="Patient",
            family_name="Family",
            gender=GenderEnum.MALE,
            birth_date="2020-03-29",
        ),
        "3656fe3b-09f7-40d0-8f4a-608245fd3c4c": Patient(
            id=UUID("3656fe3b-09f7-40d0-8f4a-608245fd3c4c"),
            primary_identifier="PID-2",
            active=True,
            given_name="Patienta",
            family_name="Family",
            gender=GenderEnum.FEMALE,
            birth_date="2020-03-29",
        ),
    }
    for p in context.patients_by_id.values():
        context.db.add(p)

    context.db.add(context.patient_to_delete)
    context.db.commit()


@step("several patients exist, not including ID to be deleted")
def step_impl(context):
    context.patients_by_id = {
        "00e72ed2-159f-48af-8832-56da41d35a0e": Patient(
            id=UUID("00e72ed2-159f-48af-8832-56da41d35a0e"),
            primary_identifier="PID-1",
            active=True,
            given_name="Patient",
            family_name="Family",
            gender=GenderEnum.MALE,
            birth_date="2020-03-29",
        ),
        "3656fe3b-09f7-40d0-8f4a-608245fd3c4c": Patient(
            id=UUID("3656fe3b-09f7-40d0-8f4a-608245fd3c4c"),
            primary_identifier="PID-2",
            active=True,
            given_name="Patienta",
            family_name="Family",
            gender=GenderEnum.FEMALE,
            birth_date="2020-03-29",
        ),
    }
    for p in context.patients_by_id.values():
        context.db.add(p)
    context.db.commit()


@when("the request is made to delete patient by id")
def step_impl(context):
    context.response = context.client.post(**context.request)


@step("the deleted patient no longer exists")
def step_impl(context):
    engine = get_new_db_engine()
    session = get_new_db_session(engine)
    patient = session.get(Patient, context.del_patient_id)

    assert not patient

    for patient in context.patients_by_id.values():
        p = session.get(Patient, patient.id)
        assert p
    session.close()


@step("no patients were deleted")
def step_impl(context):
    for patient in context.patients_by_id.values():
        p = context.db.get(Patient, patient.id)
        assert p


@step("the delete patient event is published")
def step_impl(context):
    topic = config.PATIENT_PUBLISHER_AUDIT_TRAIL_STREAM_NAME
    value = {
        "entity_id": "445b234b-ab5a-49e7-a6e8-6b81fe513862",
        "event_name": "Patient Deleted",
        "performed_on": AnyDateTime(),
        "performed_by": "b4f6f4e0-6ca5-4be9-99d4-28d66bd82ecd",
        "event_state": {
            "id": "445b234b-ab5a-49e7-a6e8-6b81fe513862",
            "primary_identifier": "PID-3",
            "active": True,
            "given_name": "PatientD",
            "family_name": "family",
            "gender": "male",
            "birth_date": "2020-03-29",
        },
        "previous_state": {
            "id": "445b234b-ab5a-49e7-a6e8-6b81fe513862",
            "primary_identifier": "PID-3",
            "active": True,
            "given_name": "PatientD",
            "family_name": "family",
            "gender": "male",
            "birth_date": "2020-03-29",
        },
        "entity_name": "patient",
        "emitted_by": "patient",
        "event_type": "PATIENT_DELETED_EVENT",
        "message_id": AnyUUID(),
        "event_data": {},
    }
    headers = [("event_type", b"PATIENT_DELETED_EVENT")]
    assert_message_was_published(context, topic, value, headers)


@step("physiological alerts have been triggered for the patient")
def step_impl(context):
    active_alert = PhysiologicalAlertFactory(active=True, patient_id=context.patient_to_delete.id)
    inactive_alert = PhysiologicalAlertFactory(
        patient_id=context.patient_to_delete.id,
        code=active_alert.code,
        device_primary_identifier=active_alert.device_primary_identifier,
        determination_time=active_alert.determination_time + timedelta(hours=1),
        active=False,
    )
    context.db.add(active_alert)
    context.db.add(inactive_alert)
    context.db.commit()


@step("the patient has observations assigned")
def step_impl(context):
    for i in range(5):
        obs = ObservationFactory.build(
            subject_id=UUID(context.del_patient_id),
        )
        context.db.add(obs)
        context.db.flush()
    context.db.commit()
