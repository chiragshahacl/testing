import respx
import yaml
from behave import step
from fastapi import status
from httpx import Response
from test_tools import assert_deep_equal

from src.settings import settings


@step("a request to get EHR patients with the following parameters")
def setup_ehr_request(context):
    context.params = yaml.safe_load(context.text)
    context.request = {"url": "/web/patient/ehr", "params": context.params}


@step("the request to get EHR patient is made")
def request_ehr_patients(context):
    context.response = context.client.get(**context.request)


@step("there are patients in the EHR")
def mock_get_ehr_patients_request(context):
    context.ehr_patients = [
        {
            "patientIdentifiers": ["123"],
            "givenName": "John",
            "familyName": "Doe",
            "birthDate": "2020-01-01",
            "gender": "M",
        },
        {
            "patientIdentifiers": ["456"],
            "givenName": "Jane",
            "familyName": "Doe",
            "birthDate": "1970-01-01",
            "gender": "F",
        },
    ]
    ehr_query_params = {**context.params} if context.params else {}
    if context.params and context.params.get("birthDate"):
        ehr_query_params["birthDate"] = ehr_query_params["birthDate"].replace("-", "")

    context.ehr_patient_request = respx.get(
        f"{settings.EHR_PLATFORM_BASE_URL}/query/patient/", params=ehr_query_params
    ).mock(
        Response(
            json={"resources": context.ehr_patients},
            status_code=status.HTTP_200_OK,
        )
    )


@step("the patients are in the response")
def check_ehr_patient_response(context):
    assert_deep_equal(context.response.json()["resources"], context.ehr_patients)


@step("some EHR patients are being monitored")
def step_impl(context):
    context.monitored_patients = getattr(context, "monitored_patients", [])
    context.monitored_patients.append("123")
    context.cache.set(f"{settings.REDIS_SHARED_CACHE_PREFIX}/123", "PM-001")


@step("the monitored patients are not in the response")
def step_impl(context):
    resources = context.response.json()["resources"]
    found_ids = [p["patientIdentifiers"][0] for p in resources]
    for monitored_identifier in context.monitored_patients:
        assert monitored_identifier not in found_ids
