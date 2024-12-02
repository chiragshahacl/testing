import respx
from behave import step, when
from httpx import Response
from starlette import status
from test_tools import assert_deep_equal

from common import generate_valid_jwt_token
from src.settings import settings


@step("a request to create a patient")
def step_impl(context):
    token = generate_valid_jwt_token(context)
    context.valid_token = token
    context.patient_primary_identifier = "patient-1"
    context.patient_given_name = "patient"
    context.patient_family_name = "sibel"
    context.patient_active = True
    context.patient_gender = "male"
    context.patient_birthdate = "2020-03-29"
    context.request = {
        "headers": {"Authorization": context.valid_token},
        "url": "/web/patient",
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
def step_impl(context):
    token = generate_valid_jwt_token(context)
    context.valid_token = token
    context.patient_primary_identifier = "patient-1"
    context.patient_given_name = "patient"
    context.patient_family_name = "sibel"
    context.patient_active = True
    context.patient_gender = "male"
    context.request = {
        "headers": {"Authorization": context.valid_token},
        "url": "/web/patient",
        "json": {
            "id": context.patient_id,
            "primary_identifier": context.patient_primary_identifier,
            "active": context.patient_active,
            "given_name": context.patient_given_name,
            "family_name": context.patient_family_name,
            "gender": context.patient_gender,
        },
    }


@when("the request is made to create a patient")
def step_impl(context):
    context.response = context.client.post(**context.request)


@step("the patient is created")
def step_impl(context):
    response = context.response.json()

    assert_deep_equal(
        response,
        {
            "id": context.patient_id,
            "primary_identifier": context.patient_primary_identifier,
            "active": context.patient_active,
            "given_name": context.patient_given_name,
            "family_name": context.patient_family_name,
            "gender": context.patient_gender,
            "birth_date": context.patient_birthdate
            if hasattr(context, "patient_birthdate")
            else None,
        },
    )


@step("the patient to be created does not exist")
def step_impl(context):
    respx.post(
        f"{settings.PATIENT_PLATFORM_BASE_URL}/CreatePatient",
    ).mock(
        return_value=Response(
            status_code=status.HTTP_200_OK,
            json=context.request["json"],
        )
    )


@step("the patient to be created exists")
def step_impl(context):
    respx.post(
        f"{settings.PATIENT_PLATFORM_BASE_URL}/CreatePatient",
    ).mock(
        return_value=Response(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            json={"details": [{"loc": ["string"], "msg": "string", "type": "string", "ctx": {}}]},
        ),
    )
