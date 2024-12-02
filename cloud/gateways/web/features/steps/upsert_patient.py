import respx
from behave import step, then, when
from httpx import Response
from starlette import status

from common import generate_valid_jwt_token
from src.settings import settings


@step("a request to upsert a patient")
def step_impl(context):
    token = generate_valid_jwt_token(context)
    context.valid_token = token
    context.patient_primary_identifier = "patient-1"
    context.patient_given_name = "patient"
    context.patient_new_given_name = "new patient"
    context.patient_family_name = "sibel"
    context.patient_active = True
    context.patient_gender = "male"
    context.patient_birthdate = "2020-03-29"
    context.request = {
        "url": "/web/patient",
        "headers": {"Authorization": context.valid_token},
        "json": {
            "id": context.patient_id,
            "primary_identifier": context.patient_primary_identifier,
            "active": context.patient_active,
            "given_name": context.patient_new_given_name,
            "family_name": context.patient_family_name,
            "gender": context.patient_gender,
            "birth_date": context.patient_birthdate,
        },
    }


@step("a request to upsert a patient is invalid")
def step_impl(context):
    token = generate_valid_jwt_token(context)
    context.valid_token = token
    context.patient_primary_identifier = "patient-1"
    context.patient_given_name = "patient"
    context.patient_new_given_name = "new patient"
    context.patient_family_name = "sibel"
    context.patient_active = True
    context.patient_gender = "male"
    context.patient_birthdate = "2020-03-29"
    context.request = {
        "url": "/web/patient",
        "headers": {"Authorization": context.valid_token},
        "json": {
            "primary_identifier": context.patient_primary_identifier,
            "active": context.patient_active,
            "given_name": context.patient_new_given_name,
            "family_name": context.patient_family_name,
            "gender": context.patient_gender,
            "birth_date": context.patient_birthdate,
        },
    }


@when("the request is made to upsert a patient")
def step_impl(context):
    context.response = context.client.put(**context.request)


@step("the patient to be upserted does not exist")
def step_impl(context):
    respx.get(
        f"{settings.PATIENT_PLATFORM_BASE_URL}/identifier/{context.patient_primary_identifier}"
    ).mock(Response(status_code=status.HTTP_404_NOT_FOUND))

    respx.post(
        f"{settings.PATIENT_PLATFORM_BASE_URL}/CreatePatient",
    ).mock(
        return_value=Response(
            json={
                "id": context.patient_id,
                "primary_identifier": context.patient_primary_identifier,
                "active": context.patient_active,
                "given_name": context.patient_given_name,
                "family_name": context.patient_family_name,
                "gender": context.patient_gender,
                "birth_date": context.patient_birthdate,
            },
            status_code=status.HTTP_200_OK,
        )
    )


@step("the patient to be upserted exists")
def step_impl(context):
    respx.get(
        f"{settings.PATIENT_PLATFORM_BASE_URL}/identifier/{context.patient_primary_identifier}",
    ).mock(
        Response(
            json={
                "id": context.patient_id,
                "primary_identifier": context.patient_primary_identifier,
                "active": context.patient_active,
                "given_name": context.patient_given_name,
                "family_name": context.patient_family_name,
                "gender": context.patient_gender,
                "birth_date": context.patient_birthdate,
            },
            status_code=status.HTTP_200_OK,
        )
    )
    respx.post(
        f"{settings.PATIENT_PLATFORM_BASE_URL}/UpdatePatientInfo",
        json={
            "id": context.patient_id,
            "primary_identifier": context.patient_primary_identifier,
            "active": context.patient_active,
            "given_name": context.patient_new_given_name,
            "family_name": context.patient_family_name,
            "gender": context.patient_gender,
            "birth_date": context.patient_birthdate,
        },
    ).mock(
        return_value=Response(
            json={
                "id": context.patient_id,
                "primary_identifier": context.patient_primary_identifier,
                "active": context.patient_active,
                "given_name": context.patient_new_given_name,
                "family_name": context.patient_family_name,
                "gender": context.patient_gender,
                "birth_date": context.patient_birthdate,
            },
            status_code=status.HTTP_200_OK,
        )
    )


@then("the user is told the patient was updated")
def step_impl(context):
    assert context.response.status_code == status.HTTP_200_OK


@step("the user is told the patient was created")
def step_impl(context):
    assert context.response.status_code == status.HTTP_201_CREATED
