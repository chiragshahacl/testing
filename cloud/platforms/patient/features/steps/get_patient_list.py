from uuid import UUID

from behave import step, then, when
from sqlalchemy import func

from app.common.models import Patient
from app.patient.enums import GenderEnum


@step("a request to get list of all patients")
def step_impl(context):
    context.request = {"url": "/patient"}


@step("a request to get patients count")
def step_impl(context):
    context.request = {"url": "/patient/count"}


@when("the request for all patients is made")
def step_impl(context):
    context.response = context.client.get(
        **context.request, params=getattr(context, "query_params", {})
    )


@then("the list of all patients is returned")
def step_impl(context):
    resp = context.response.json()
    assert isinstance(resp, dict)
    assert isinstance(resp["resources"], list)
    assert len(resp["resources"]) == len(list(context.patients_by_id.values()))
    for org in resp["resources"]:
        assert "id" in org
        assert org["id"] in context.patients_by_id

        expected_patient = context.patients_by_id[org["id"]]
        assert str(expected_patient.id) == org["id"]
        assert expected_patient.active == org["active"]
        assert expected_patient.given_name == org["given_name"]
        assert expected_patient.family_name == org["family_name"]
        assert expected_patient.gender.value == org["gender"]
        assert str(expected_patient.birth_date) == org["birth_date"]


@then("an empty list of all patients is returned")
def step_impl(context):
    resp = context.response.json()
    resp["resources"] = []
    assert isinstance(resp, dict)
    assert isinstance(resp["resources"], list)
    assert len(resp["resources"]) == 0


@step("several patients exist")
@step("several patients exist including one with identifier `{identifier}`")
def step_impl(context, identifier="PID-1"):
    context.patients_by_id = {
        "00e72ed2-159f-48af-8832-56da41d35a0e": Patient(
            id=UUID("00e72ed2-159f-48af-8832-56da41d35a0e"),
            primary_identifier=identifier,
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


@step("the first `{num_patients}` patients are returned")
def step_impl(context, num_patients):
    expected_patients = (
        context.db.query(Patient)
        .order_by(Patient.primary_identifier)
        .limit(int(num_patients))
        .all()
    )
    returned_patients = context.response.json()["resources"]
    assert len(returned_patients) == len(expected_patients)

    expected_patient_ids = {str(p.id) for p in expected_patients}
    returned_patient_ids = {p["id"] for p in returned_patients}
    for patient_id in returned_patient_ids:
        assert patient_id in expected_patient_ids


@step("the second page patients are returned")
def step_impl(context):
    expected_patients = (
        context.db.query(Patient).order_by(Patient.primary_identifier).offset(5).all()
    )
    returned_patients = context.response.json()["resources"]
    assert len(returned_patients) == len(expected_patients)

    expected_patient_ids = {str(p.id) for p in expected_patients}
    returned_patient_ids = {p["id"] for p in returned_patients}
    for patient_id in returned_patient_ids:
        assert patient_id in expected_patient_ids


@step("all the patients with identifier `{identifier}` are returned")
def step_impl(context, identifier):
    resources = context.response.json()
    patients = resources["resources"]
    assert len(patients) == 1
    assert patients[0]["primary_identifier"] == identifier


@step("the total number of resources is specified")
def step_impl(context):
    num_patients = context.db.query(func.count(Patient.id)).scalar()
    assert context.response.json()["total"] == num_patients


@step("the total number of resources is `{number}`")
def step_impl(context, number):
    assert context.response.json()["total"] == int(number)
