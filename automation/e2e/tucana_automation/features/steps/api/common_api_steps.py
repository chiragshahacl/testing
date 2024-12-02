import json
import logging

import requests
from behave import *

from utils.api_utils import get_access_token, raise_http_error, requests_get, requests_delete_batch, requests_delete

requests.packages.urllib3.disable_warnings()


@step("the Tucana application is running")
def tucana_health(context):
    response = requests_get(context, "/web/health")
    if response.status_code == 200:
        status = response.json()["status"]
        assert "Healthy" in status, "The application is not running properly"
    else:
        raise_http_error(response)


@step("the user credentials are valid")
def valid_user_credentials(context):
    response = get_access_token(context)
    assert response.status_code == 200, "Couldn't get the Token"
    response_jsonify = json.loads(response.text)
    context.access_token = response_jsonify["access"]
    context.refresh_token = response_jsonify["refresh"]


@step("authentication credentials are being included")
def authentication_included(context):
    if "access_token" not in context:
        context.access_token = valid_user_credentials(context)


@step("the credentials are not valid")
def not_valid_credentials(context):
    context.access_token = "eyJhbGciOiJSUzI1NiIsInR5cCI6IkpXVCJ9.eyJ0b2tlbl90eXBlIjoiYWNjZXNzIiwiZXhwIjoxNjg0NjE3OTg1LCJpYXQiOjE2ODQ1MzE1ODUsImp0aSI6ImY1ZjUxYzQxYmJkNzRhYzViYTQ5ODAyYzQxNzQyYmZmIiwidXNlcl9pZCI6IjdiNTVlZmIyLWE3NjctNGQ5Yy1iNzc3LWQ1NjY3NTc0NjJkNiIsInVzZXJuYW1lIjoiYWRtaW5Ac2liZWxoZWFsdGguY29tIiwiZ3JvdXBzIjpbImFkbWluIl0sImF1ZCI6InR1Y2FuYSJ9.YknuyOLqwKcJyU0CvzROuAR7e8faljdNvnoYjJP6HDhw_oDVHUktQmVGEL1ah_sApLHVz0j3RH9eHkHc4DEtDpa5y8CZAB3aY4q7RfK9D7O6rD_45UAR1ilKgPV6T-POsTcZqME7nKck6k1K0ajaSVsxTODC8fZuId5l4-i2gg56iiVJPSgz72xCYzbLlVdWT2Be3sF6M65otCk2mbAj3VAwJXFXSYD6vc5k6tSCv-DjyzguiUv-ZubAxPgO-WLWZF2-eChAjr9hialmSYoUa49hCZmaJ3s8GrhQD4HJ6qdSHL_OjpIxJgMJhKY4eYGNCdOKQvPQdAWJTmWSPUqIcc"


@step("authentication credentials are not being included")
def authentication_not_included(context):
    context.no_auth = True


@step("the user is told the request was unauthorized")
@step("the user is informed that the request to refresh the token was unauthorized")
@step("the user is told their password is incorrect")
def verify_request_status_unauthorized(context):
    assert (
            context.response.status_code == 401
    ), "Expected status code 401, current " + str(context.response.status_code)
    assert context.response.reason == "Unauthorized", (
            "Expected reason unauthorized, current " + context.response.reason
    )


@step("the user is told the request was forbidden")
def verify_request_status_forbidden(context):
    assert (
            context.response.status_code == 403
    ), "Expected status code 403, current " + str(context.response.status_code)
    assert context.response.reason == "Forbidden", (
            "Expected reason forbidden, current " + context.response.reason
    )


@step("the user is told their payload is invalid")
@step("the user is told their password is invalid")
def verify_request_status_forbidden(context):
    assert (
            context.response.status_code == 422
    ), "Expected status code 422, current " + str(context.response.status_code)
    assert context.response.reason == "Unprocessable Entity", (
            "Expected reason Unprocessable Entity, current " + context.response.reason
    )


@step("the user is told the request to delete was successful")
@step(
    "the user is told the request to create a new bed through upsert endpoint was successful"
)
@step(
    "the user is told the request to update a bed through upsert endpoint was successful"
)
@step(
    "the user is told the request to create a new bed group through upsert endpoint was successful"
)
@step(
    "the user is told the request to update a bed group through upsert endpoint was successful"
)
@step("the user is told the request to assign was successful")
@step("the user is informed that the logout was successful")
@step("the user is told the request to create a new device was successful")
@step("the user is told the request to assign bed to a device was successful")
def verify_delete_request_status(context):
    try:
        assert (
                context.response.status_code == 204
        ), "Expected status code 204, current " + str(context.response.status_code)
    except AssertionError:
        if len(json.loads(context.response.text)['detail']) > 0:
            raise Exception(json.loads(context.response.text)['detail'][0]['msg'])
    assert context.response.reason == "No Content", (
            "Expected reason OK, current " + context.response.reason
    )


@step("the user is told the request to create was successful")
@step("the user is told the get patient request was successful")
@step("the user is told the request to get the list of the bed group was successful")
@step("the user is told the request to get the list of beds was successful")
@step("the user is told the request to get the list of patients was successful")
@step("the user is told the request to update was successful")
@step("the user is told the request to refresh the token was successful")
@step("the user is told the request to get the list of devices was successful")
@step("the user is told the get audit trail request was successful")
@step("the user is told the request to get the bed group observations was successful")
@step(
    "the user is told the request to get the vital ranges list of devices was successful"
)
@step("Tom is told the get patient session alerts request was successful")
@step("Tom is told the get bed group observations request was successful")
def create_entity_response(context):
    assert (
            context.response.status_code == 200
    ), f"Expected status code 200, current {context.response.status_code}"
    assert (
            context.response.reason == "OK"
    ), f"Expected reason OK, current {context.response.reason}"


@step("the user is told the request was successful")
def request_success(context):
    assert (
            context.response.status_code == 201
    ), f"Expected status code 201, current {context.response.status_code}"
    assert (
            context.response.reason == "Created"
    ), f"Expected reason Created, current {context.response.reason}"


def verify_request_status(context, status, reason):
    assert context.response.status_code == status, (
            f"Expected status code "
            + {status}
            + ", current "
            + {context.response.status_code}
    )
    assert context.response.reason == reason, (
            f"Expected reason " + {reason} + ", current " + {context.response.reason}
    )


@step("Tom deletes all the created scenario data")
def deletes_all_data(context):
    try:
        if len(context.patient_bed_and_group) > 0:
            for key, value in context.patient_bed_and_group.copy().items():
                if key == 'bed':
                    context.data = {"url": "/web/bed/batch", "json": {"bed_ids": [value]}}
                    url = context.data["url"]
                    context.response = requests_delete_batch(
                        context, url, context.data["json"], headers=None
                    )
                    verify_delete_request_status(context)
                    logging.info(f'Bed {value} deleted')
                    context.patient_bed_and_group.pop('bed')
                elif key == 'group':
                    context.data = {
                        "url": "/web/bed-group/batch",
                        "json": {
                            "group_ids": [value]
                        },
                    }
                    url = context.data["url"]
                    context.response = requests_delete_batch(context, url, context.data["json"], headers=None)
                    verify_delete_request_status(context)
                    logging.info(f'Group {value} deleted')
                    context.patient_bed_and_group.pop('group')
                elif key == 'patient':
                    context.response = requests_delete(context, "web/patient/{}".format(value), headers=None)
                    verify_delete_request_status(context)
                    logging.info(f'Patient {value} deleted')
                    context.patient_bed_and_group.pop('patient')
    except Exception:
        raise Exception('Something went wrong deleting patient/bed/group information')


@step("the information is saved")
def saves_bed_group(context):
    context.patient_bed_and_group['bed'] = context.bed_id
    context.patient_bed_and_group['group'] = context.bed_group_id
