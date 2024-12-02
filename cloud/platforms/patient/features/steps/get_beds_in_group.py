import uuid
from datetime import datetime, timezone

from behave import step, when
from sqlalchemy import select

from app.common.models import BedGroup, Patient
from app.device.src.common.models import Device
from app.encounter.enums import EncounterStatus
from app.encounter.models import Encounter
from app.patient.enums import GenderEnum


@step("a request to get all beds in a group")
def step_impl(context):
    context.group_id = "33290266-1e57-46a4-888a-d900ceeadd47"
    context.group_ids = [context.group_id]
    context.request = {"url": f"/patient/bed-group/{context.group_id}/beds"}


@when("the request to get bed group beds is made")
def step_impl(context):
    context.response = context.client.get(**context.request)
    context.db.expire_all()


@step("the bed group beds are returned")
def step_impl(context):
    found_group = (
        context.db.execute(
            select(BedGroup).join(BedGroup.beds).where(BedGroup.id == context.group_id)
        )
        .scalars()
        .first()
    )
    expected_beds = found_group.beds
    found_beds = context.response.json()["resources"]
    assert len(expected_beds) == len(found_beds)
    found_beds_by_id = {bed["id"]: bed for bed in found_beds}
    for bed in expected_beds:
        bed = found_beds_by_id[str(bed.id)]
        assert "patient" in bed
        expected_patient = context.patients_by_bed_id.get(str(bed["id"]))
        if expected_patient:
            assert str(expected_patient.id) == bed["patient"]["id"]
        expected_encounter = context.encounters_by_bed_id.get(str(bed["id"]))
        if expected_encounter:
            assert str(expected_encounter.id) == bed["encounter"]["id"]
            assert expected_encounter.status == bed["encounter"]["status"]


@step("the beds have patients assigned")
@step("the beds have patients assigned with status `{encounter_status}`")
def step_impl(context, encounter_status: str = EncounterStatus.IN_PROGRESS.value):
    encounter_status = EncounterStatus(encounter_status)
    context.patients_by_bed_id = {}
    context.encounters_by_bed_id = {}
    for index, bed in enumerate(context.assigned_beds):
        context.db.add(bed)
        context.db.flush()
        patient = Patient(
            id=uuid.uuid4(),
            primary_identifier=f"PX-{index}",
            active=True,
            given_name="Patient",
            family_name="Family",
            gender=GenderEnum.FEMALE,
            birth_date="2020-03-29",
        )
        context.db.add(patient)
        context.db.flush()
        device = Device(
            id=uuid.uuid4(),
            primary_identifier=f"PM-{index}",
            name="Patient Monitor",
            model_number="Patient Monitor",
            location_id=bed.id,
        )
        context.db.add(device)
        context.db.flush()
        encounter = Encounter(
            id=uuid.uuid4(),
            subject_id=patient.id,
            device_id=device.id,
            status=encounter_status,
            start_time=datetime.now(timezone.utc),
        )
        context.db.add(encounter)
        context.db.flush()
        context.patients_by_bed_id[str(bed.id)] = patient
        context.encounters_by_bed_id[str(bed.id)] = encounter
    context.db.commit()
