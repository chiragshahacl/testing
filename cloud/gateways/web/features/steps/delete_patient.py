import respx
from behave import step, when
from httpx import Response
from starlette import status

from src.settings import settings


@step("a request to delete a patient")
def step_impl(context):
    context.patient_id = "e450e7d7-135f-46ff-83c7-0cda5308c12c"
    context.request = {"url": f"/web/patient/{context.patient_id}"}


@step("the patient doesnt exist")
def step_impl(context):
    respx.post(f"{settings.PATIENT_PLATFORM_BASE_URL}/DeletePatient").mock(
        return_value=Response(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            json={"details": [{"loc": ["string"], "msg": "string", "type": "string", "ctx": {}}]},
        )
    )


@step("the patient exists")
def step_impl(context):
    respx.post(f"{settings.PATIENT_PLATFORM_BASE_URL}/DeletePatient").mock(
        return_value=Response(
            status_code=status.HTTP_204_NO_CONTENT,
        )
    )


@when("the request is made to delete a patient")
def step_impl(context):
    context.response = context.client.delete(**context.request)
