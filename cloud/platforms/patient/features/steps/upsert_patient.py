from behave import step, then
from test_tools import assert_contains

from app.common.models import Patient
from app.patient.enums import GenderEnum


@step("a request to create a patient")
def create_patient(context):
    context.patient_id = "7ab46f31-c98d-4c19-b720-798972787459"
    context.patient_primary_identifier = "primary-identifier"
    context.patient_active = True
    context.patient_given_name = "given"
    context.patient_family_name = "family"
    context.patient_gender = "male"
    context.patient_birthdate = "2020-03-29"
    context.request = {
        "url": "/patient/CreatePatient",
        "json": {
            "id": context.patient_id,
            "primary_identifier": context.patient_primary_identifier,
            "active": context.patient_active,
            "given_name": context.patient_given_name,
            "family_name": context.patient_family_name,
            "gender": context.patient_gender,
            "birth_date": context.patient_birthdate,
        },
    }


@step("a request to create a patient without birthdate")
def new_patient_without_birthdate(context):
    context.patient_id = "7ab46f31-c98d-4c19-b720-798972787459"
    context.patient_primary_identifier = "primary-identifier"
    context.patient_active = True
    context.patient_given_name = "given"
    context.patient_family_name = "family"
    context.patient_gender = "male"
    context.request = {
        "url": "/patient/CreatePatient",
        "json": {
            "id": context.patient_id,
            "primary_identifier": context.patient_primary_identifier,
            "active": context.patient_active,
            "given_name": context.patient_given_name,
            "family_name": context.patient_family_name,
            "gender": context.patient_gender,
        },
    }


@step("a patient with the same id already exists")
def create_same_id_patient(context):
    patient = Patient(
        id=context.patient_id,
        primary_identifier="primary-identifier",
        active=True,
        given_name="given-name",
        family_name="family-name",
        gender=GenderEnum["FEMALE"],
        birth_date="2020-03-29",
    )
    context.db.add(patient)
    context.db.commit()


@step("a patient with the same primary identifier already exists for the tenant")
def create_same_identifier_patient(context):
    patient = Patient(
        id="adff0e23-aef4-4702-b739-5d5dda4e8838",
        primary_identifier=context.patient_primary_identifier,
        active=True,
        given_name="given-name",
        family_name="family-name",
        gender=GenderEnum.FEMALE,
    )
    context.db.add(patient)
    context.db.commit()


@step("a patient with the same primary identifier already exists for other tenant")
def create_same_identifier_patient_different_tenant(context):
    patient = Patient(
        id="645b68d0-3628-4c86-8fc8-9e2654ebad20",
        primary_identifier=context.patient_primary_identifier,
        active=True,
        given_name="given-name",
        family_name="family-name",
        gender=GenderEnum.FEMALE,
        birth_date="2020-03-29",
    )
    context.db.add(patient)
    context.db.commit()


@then("the patient is not created")
def check_patient_not_created(context):
    patient = context.db.get(Patient, context.patient_id)
    assert not patient


@step("a new active status is provided")
def set_new_status(context):
    context.patient_active = not context.patient_active
    context.request["json"]["active"] = context.patient_active


@step("a new given_name is provided")
def set_new_given_name(context):
    context.patient_given_name = "new-given-name"
    context.request["json"]["given_name"] = context.patient_given_name


@step("a new family_name is provided")
def set_new_family_name(context):
    context.patient_family_name = "new-family-name"
    context.request["json"]["family_name"] = context.patient_family_name


@step("a new gender is provided")
def set_new_gender(context):
    context.patient_gender = "other"
    context.request["json"]["gender"] = context.patient_gender


@step("a new birthdate is provided")
def set_new_birthdate(context):
    context.patient_birthdate = "2021-03-29"
    context.request["json"]["birth_date"] = context.patient_birthdate


@step("a new patient_identifier is provided")
def set_new_identifier(context):
    context.patient_primary_identifier = "primary-identifier"
    context.request["json"]["primary_identifier"] = context.patient_primary_identifier


@step("the new patient is returned")
def check_new_patient(context):
    resp = context.response.json()

    assert_contains(
        resp,
        {
            "id": "7ab46f31-c98d-4c19-b720-798972787459",
            "active": True,
            "given_name": "given",
            "family_name": "family",
            "gender": "male",
            "primary_identifier": "primary-identifier",
            "birth_date": context.patient_birthdate
            if hasattr(context, "patient_birthdate")
            else None,
        },
    )


@step("the updated patient is returned")
def check_updated_patient(context):
    resp = context.response.json()

    assert_contains(
        resp,
        {
            "id": "7ab46f31-c98d-4c19-b720-798972787459",
            "active": False,
            "given_name": "new-given-name",
            "family_name": "new-family-name",
            "gender": "other",
            "primary_identifier": "primary-identifier",
            "birth_date": str(
                context.patient_birthdate if hasattr(context, "patient_birthdate") else None
            ),
        },
    )
