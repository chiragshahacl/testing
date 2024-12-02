from behave import step, when
from test_tools import assert_contains

from app.encounter.enums import EncounterStatus
from features.environment import AnyDateTime
from features.factories.bed_factories import BedFactory
from features.factories.device_factories import DeviceFactory
from features.factories.encounter import EncounterFactory
from features.factories.patient_factories import PatientFactory


@step("a device with an encounter assigned exists")
def step_impl(context):
    context.bed = BedFactory.build()
    context.db.add(context.bed)
    context.db.commit()

    context.device = DeviceFactory.build(location_id=context.bed.id)
    context.db.add(context.device)
    context.db.commit()

    context.patient = PatientFactory.build()
    context.db.add(context.patient)
    context.db.commit()

    context.encounter_status = EncounterStatus.PLANNED
    context.encounter = EncounterFactory.build(
        device=context.device,
        subject=context.patient,
        status=context.encounter_status,
        start_time=None,
        end_time=None,
    )
    context.db.add(context.encounter)
    context.db.commit()


@step("a request to get the admission of the device")
def step_get_admission_of_device_request(context):
    if not hasattr(context, "device"):
        raise ValueError("A device needs to be created before running this step")

    context.request = {"url": f"/device/{str(context.device.primary_identifier)}/admission"}


@when("the request is made to get the admission")
def step_impl(context):
    context.response = context.client.get(**context.request)


@step("the admission is returned")
def step_impl(context):
    resp = context.response.json()
    expected = {
        "resource": {
            "id": str(context.encounter.id),
            "subject": {
                "id": str(context.patient.id),
                "primary_identifier": context.patient.primary_identifier,
                "active": context.patient.active,
                "given_name": context.patient.given_name,
                "family_name": context.patient.family_name,
                "gender": context.patient.gender.value,
                "birth_date": str(context.patient.birth_date),
            },
            "device": {
                "id": str(context.device.id),
                "primary_identifier": context.device.primary_identifier,
                "name": context.device.name,
                "gateway_id": None,
                "location_id": str(context.bed.id),
                "audio_pause_enabled": True,
                "audio_enabled": False,
                "subject_identifier": None,
                "model_number": context.device.model_number,
            },
            "created_at": context.encounter.created_at.isoformat(sep="T", timespec="auto"),
            "status": EncounterStatus.PLANNED.value,
            "start_time": None,
            "end_time": None,
        }
    }

    assert_contains(resp, expected)


@step("a device without any encounter assigned exists")
def create_device_without_encounter(context):
    context.bed = BedFactory.build()
    context.db.add(context.bed)
    context.db.commit()

    context.device = DeviceFactory.build(location_id=context.bed.id)
    context.db.add(context.device)
    context.db.commit()


@step("the empty admission is returned")
def step_impl(context):
    resp = context.response.json()
    expected = {"resource": None}

    assert_contains(resp, expected)
