import json
import logging
import uuid

from faker import Faker

from utils.api_utils import get_access_token, requests_delete_batch, requests_post, requests_put, requests_get


def create_bed(context):
    logging.getLogger("faker").setLevel(logging.ERROR)
    faker = Faker()
    context.bed_hook_name = faker.bothify("BED-QA-HOOK-#####")
    context.data = {
        "url": "/web/bed/batch",
        "json": {"resources": [{"name": context.bed_hook_name}]},
    }
    get_token_in_hook(context)
    url = context.data["url"]
    context.response = requests_post(context, url, context.data["json"], headers=None)
    assert (
            context.response.status_code == 200
    ), f"Expected status code 200, current {context.response.status_code}"
    assert (
            context.response.reason == "OK"
    ), f"Expected reason OK, current {context.response.reason}"
    logging.info(f"[HOOK] Bed {context.bed_hook_name} created correctly on ")
    bed_created = context.response.json()
    context.bed_hook_id = bed_created["resources"][0]["id"]
    context.bed_hook_ids.append(context.bed_hook_id)


def create_pm(context):
    logging.getLogger("faker").setLevel(logging.ERROR)
    faker = Faker()
    # Create Extra PM to assure all banners and tests
    pm_id = faker.bothify("PM-QA-HOOK_X####")
    context.pm_hook_uuid = str(uuid.uuid4())
    data = {
        "id": context.pm_hook_uuid,
        "name": pm_id,
        "primary_identifier": pm_id,
        "device_code": "Patient Monitor"
    }
    url = "/web/device"
    context.response = requests_put(context, url, data, headers=None)

    assert context.response.status_code == 204, f'Can not create the PM {pm_id} at BeforeAll Hook, PM Already existent?, REMOVE IT FIRST'
    logging.info(f'[HOOK] Created PM device with id {context.pm_hook_uuid}')
    context.pm_hook_ids[pm_id] = context.pm_hook_uuid


def create_bed_and_pm_through_api(context):
    create_bed(context)
    create_pm(context)


def assign_bed_to_pm(context):
    logging.info(f'[HOOK] Assigning Bed to PM ***')
    context.data = {
        "url": "/web/device/bed/batch",
        "json": {
            "associations": [
                {"bed_id": context.bed_hook_id, "device_id": context.pm_hook_uuid},
            ]
        },
    }
    url = context.data["url"]
    context.response = requests_put(context, url, context.data["json"], headers=None)
    assert context.response.status_code == 204, "Expected status code 204, current " + str(context.response.status_code)
    logging.info(f'[HOOK] Bed assigned to PM correctly ***')


def clean_all_through_api(context):
    get_token_in_hook(context)
    for bed_hook_id in context.bed_hook_ids:
        context.data = {"url": "/web/bed/batch", "json": {"bed_ids": [bed_hook_id]}}
        url = context.data["url"]
        context.response = requests_delete_batch(context, url, context.data["json"], headers=None)
        assert (context.response.status_code == 204), "Expected status code 204, current " + str(context.response.status_code)
        assert context.response.reason == "No Content", ("Expected reason OK, current " + context.response.reason)
        logging.info(f"Bed {bed_hook_id} deleted correctly on after_all")

    for index, pm_hook_uuid in enumerate(context.pm_hook_ids):
        data = {"device_id": context.pm_hook_ids[pm_hook_uuid]}
        response = requests_post(context, "/emulator/proxy/device/command/DeleteDevice", data, headers=None)
        assert response.status_code == 204, "Expected status code 204, current " + str(response.status_code)
        logging.info(f"PM {pm_hook_uuid} deleted correctly on after_all")


def get_token_in_hook(context):
    response = get_access_token(context)
    assert response.status_code == 200, "Couldn't get the Token"
    response_jsonify = json.loads(response.text)
    context.access_token = response_jsonify["access"]
