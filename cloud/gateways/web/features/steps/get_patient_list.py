import respx
from behave import step
from httpx import Response
from starlette import status
from test_tools import assert_deep_equal

from common import generate_valid_jwt_token
from src.settings import settings


@step("a request to get a patient list")
def step_impl(context):
    token = generate_valid_jwt_token(context)
    context.valid_token = token
    context.request = {
        "headers": {
            "Authorization": context.valid_token,
            "x-correlation-id": "30427e13-e725-4aed-9ef9-da3f421e62e4",
        },
        "url": "/web/patient",
    }


@step("a request to get a patient list without auth creds")
def step_impl(context):
    token = generate_valid_jwt_token(context)
    context.valid_token = token
    context.request = {
        "url": "/web/patient",
    }


@step("patients are found")
def step_impl(context):
    context.given_name = "Patient"
    context.family_name = "Doe"
    context.primary_identifier = "P-001"
    context.gender = "male"
    context.active = True
    context.birth_date = "2020-03-29"
    context.patients = {
        "resources": [
            {
                "given_name": context.given_name,
                "family_name": context.family_name,
                "active": context.active,
                "id": context.patient_id,
                "gender": context.gender,
                "primary_identifier": context.primary_identifier,
                "birth_date": context.birth_date,
            }
        ]
    }
    context.resp = respx.get(f"{settings.PATIENT_PLATFORM_BASE_URL}").mock(
        return_value=Response(
            status_code=status.HTTP_200_OK,
            json=context.patients,
        )
    )


@step("patients not found")
def step_impl(context):
    context.patient_id = "c8ed9893-f00b-413a-90d2-7d5191dd2ccc"
    context.patient_resource = {"resources": []}
    context.resp = respx.get(f"{settings.PATIENT_PLATFORM_BASE_URL}").mock(
        return_value=Response(
            status_code=status.HTTP_200_OK,
            json=context.patient_resource,
        )
    )


@step("the request is made to get a patient list")
def step_impl(context):
    context.response = context.client.get(**context.request)


@step("a patient list is returned")
def step_impl(context):
    resp = context.response.json()

    assert_deep_equal(
        resp,
        {
            "resources": [
                {
                    "id": context.patient_id,
                    "primaryIdentifier": context.primary_identifier,
                    "givenName": context.given_name,
                    "familyName": context.family_name,
                    "active": True,
                    "gender": context.gender,
                    "birthDate": context.birth_date,
                }
            ]
        },
    )


@step("an empty patient list is returned")
def step_impl(context):
    resp = context.response.json()
    assert len(resp["resources"]) == 0
