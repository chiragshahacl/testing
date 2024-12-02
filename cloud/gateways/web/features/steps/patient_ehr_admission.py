import uuid

import respx
from behave import step, then, when
from httpx import Response
from starlette import status

from common import generate_valid_jwt_token
from src.settings import settings


@step("a request to admit a patient via EHR search")
def step_given_a_request_to_admit_patient_ehr_search(context):
    context.valid_token = generate_valid_jwt_token(context)
    context.patient_primary_identifier = "patient-1"
    context.patient_active = True
    context.patient_given_name = "patient"
    context.patient_new_given_name = "new patient"
    context.patient_family_name = "sibel"
    context.patient_active = True
    context.patient_gender = "male"
    context.patient_birthdate = "2002-03-29"
    context.bed_id = "ec5848bb-e0fa-4100-85be-7af86dd6657c"
    context.request = {
        "url": "/web/patient/admission",
        "headers": {"Authorization": context.valid_token},
        "json": {
            "bed_id": context.bed_id,
            "payload": {
                "type": "ehr-search",
                "patientIdentifier": context.patient_primary_identifier,
                "givenName": context.patient_given_name,
                "familyName": context.patient_family_name,
                "birthDate": context.patient_birthdate,
                "gender": "M",
            },
        },
    }


@step("a request to admit a patient via quick admit")
def step_given_a_request_to_admit_patient_ehr_search(context):
    context.valid_token = generate_valid_jwt_token(context)
    context.patient_primary_identifier = "patient-1"
    context.patient_active = True
    context.patient_given_name = "patient"
    context.patient_new_given_name = "new patient"
    context.patient_family_name = "sibel"
    context.patient_active = True
    context.patient_gender = "male"
    context.patient_birthdate = "2002-03-29"
    context.bed_id = "ec5848bb-e0fa-4100-85be-7af86dd6657c"
    context.request = {
        "url": "/web/patient/admission",
        "headers": {"Authorization": context.valid_token},
        "json": {
            "bed_id": context.bed_id,
            "payload": {
                "type": "ehr-search",
                "patientIdentifier": context.patient_primary_identifier,
                "givenName": context.patient_given_name,
                "familyName": context.patient_family_name,
                "birthDate": context.patient_birthdate,
                "gender": "M",
            },
        },
    }
    respx.post(f"{settings.PATIENT_PLATFORM_BASE_URL}/PlanPatientAdmission").mock(
        return_value=Response(
            status_code=status.HTTP_204_NO_CONTENT,
        )
    )


@step("the plan patient admission request is made")
def step_plan_patient_admission_request_is_made(context):
    respx.post(
        f"{settings.PATIENT_PLATFORM_BASE_URL}/PlanPatientAdmission",
        headers={"Authorization": context.valid_token},
        json={"subject_id": context.patient_id, "bed_id": context.bed_id},
    ).mock(
        return_value=Response(
            status_code=status.HTTP_200_OK,
            json={
                "id": "3fa85f64-5717-4562-b3fc-2c963f66afa6",
                "subject_id": "3fa85f64-5717-4562-b3fc-2c963f66afa6",
                "device_id": "3fa85f64-5717-4562-b3fc-2c963f66afa6",
                "created_at": "2024-07-19T13:43:25.623Z",
                "status": "planned",
                "start_time": "2024-07-19T13:43:25.623Z",
                "end_time": "2024-07-19T13:43:25.623Z",
            },
        )
    )


@when("the request is made to for EHR patient admission")
def step_when_the_request_is_made_to_admit_patient(context):
    context.response = context.client.post(**context.request)


@then("the patient is admitted")
def step_then_the_patient_is_admitted(context):
    assert context.response.status_code == status.HTTP_204_NO_CONTENT
    assert context.response.text == ""


@step("the EHR patient is being monitored")
def step_impl(context):
    context.cache.set(
        f"{settings.REDIS_SHARED_CACHE_PREFIX}/{context.patient_primary_identifier}", "PM-001"
    )


@then("the user is told the patient is already being monitored")
def step_impl(context):
    assert context.response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
    payload = context.response.json()
    assert payload["detail"][0]["type"] == "value_error.patient_already_monitored"
