import respx
from behave import step
from httpx import Response
from starlette import status

from common import generate_valid_jwt_token
from src.settings import settings


@step("a request to get a patient")
def step_impl(context):
    token = generate_valid_jwt_token(context)
    context.valid_token = token
    context.request = {
        "headers": {"Authorization": context.valid_token},
        "url": f"/web/patient/{context.patient_id}",
    }


@step("a patient exists")
def step_impl(context):
    context.given_name = "Patient"
    context.family_name = "Doe"
    context.primary_identifier = "P-001"
    context.gender = "male"
    context.active = True
    context.patient_birthdate = "2020-03-29"
    context.patient = {
        "given_name": context.given_name,
        "family_name": context.family_name,
        "active": context.active,
        "id": context.patient_id,
        "gender": context.gender,
        "primary_identifier": context.primary_identifier,
        "birth_date": context.patient_birthdate,
    }
    context.resp = respx.get(
        f"{settings.PATIENT_PLATFORM_BASE_URL}/{context.patient_id}",
    ).mock(
        return_value=Response(
            status_code=status.HTTP_200_OK,
            json=context.patient,
        )
    )


@step("no patient exists")
def step_impl(context):
    context.patient_id = "c8ed9893-f00b-413a-90d2-7d5191dd2ccc"
    context.resp = respx.get(
        f"{settings.PATIENT_PLATFORM_BASE_URL}/{context.patient_id}",
    ).mock(
        return_value=Response(
            status_code=status.HTTP_404_NOT_FOUND,
        )
    )


@step("the request is made to get a patient")
def step_impl(context):
    context.response = context.client.get(**context.request)


@step("a patient is returned")
def step_impl(context):
    resp = context.response.json()
    assert resp
    assert resp["id"] == context.patient_id
    assert resp["primaryIdentifier"] == context.primary_identifier
    assert resp["givenName"] == context.given_name
    assert resp["familyName"] == context.family_name
    assert resp["active"] is True
    assert resp["gender"] == context.gender
    assert resp["birthDate"] == context.patient_birthdate
