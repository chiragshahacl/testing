import json
import time
import uuid

from behave import *
from faker import Faker

from features.steps.api.common_api_steps import verify_delete_request_status
from utils.api_utils import (
    requests_delete,
    requests_delete_batch,
    requests_get,
    requests_post,
    requests_put,
)

device_codes = {
    "HR": "258418",
    "RR": "258419",
    "SYS": "258421",
    "DIA": "258422",
    "SPO2": "258420",
    "PR": "258427",
    "TEMPERATURE_SKIN": "258424",
    "TEMPERATURE_BODY": "258425",
    "FALLS": "8574701",
    "POSITION_DURATION": "258426",
}


@step("A request to create a new device through Tucana's API")
def create_device(context):
    faker = Faker()
    context.device_uuid = str(uuid.uuid1())
    context.device_name = faker.bothify("QAPM-###")
    context.device_identifier = context.device_name + "-1"
    context.device_code = 'Patient Monitor'
    context.data = {
        "url": "/web/device",
        "json": {
            "id": context.device_uuid,
            "name": context.device_name,
            "primary_identifier": context.device_identifier,
            "device_code": context.device_code
        },
    }


@step("the request is made to create a device")
def send_new_device_request(context):
    url = context.data["url"]
    context.response = requests_put(context, url, context.data["json"], headers=None)


@step("the user wants to get the list of devices")
def get_devices_list(context):
    context.gateway_id = "00000000-0000-0000-0000-000000000011"
    url = "/web/device?gatewayId=" + context.gateway_id
    context.response = requests_get(context, url)


@step("the device list is received to verify the created device")
@step("devices list is received")
def verify_device_information(context):
    device_list = context.response.json()
    for index, payload_entry in enumerate(device_list["resources"]):
        payload_device_id = device_list["resources"][index]["id"]
        if context.device_uuid == payload_device_id:
            assert device_list["resources"][index]["name"] == context.device_name, (
                "The device name doesn't match, expected "
                + context.device_name
                + " current "
                + device_list["resources"][index]["name"]
            )
            assert (
                device_list["resources"][index]["primary_identifier"]
                == context.device_identifier
            ), (
                "The device primary identifier doesn't match, expected "
                + context.device_identifier
                + " current "
                + device_list["resources"][index]["primary_identifier"]
            )
            assert (
                device_list["resources"][index]["gateway_id"] == context.gateway_id
            ), (
                "The device gateway id doesn't match, expected "
                + context.gateway_id
                + " current "
                + device_list["resources"][index]["gateway_id"]
            )


@step("the device exists")
def some_device_exist(context):
    context.execute_steps(
        """ 
          Given A request to create a new device through Tucana's API
          When the request is made to create a device
          Then the user is told the request to create a new device was successful
        """
    )


@step("A request to assign bed to a device through Tucana's API")
def assign_bed_device(context):
    context.data = {
        "url": "/web/device/bed/batch",
        "json": {
            "associations": [
                {"bed_id": context.bed_id, "device_id": context.device_uuid},
            ]
        },
    }


@step("the user wants to get the list of devices filtered by bed")
def get_devices_list_filtered_by_bed(context):
    url = "/web/device?bedId=" + context.bed_id
    context.response = requests_get(context, url)


@step("the device list filtered by bed is received to verify the created device")
def verify_device_information(context):
    device_list_filtered = context.response.json()
    assert device_list_filtered["resources"]["name"] == context.device_name, (
        "The device name doesn't match, expected "
        + context.device_name
        + " current "
        + device_list_filtered["resources"]["name"]
    )
    assert (
        device_list_filtered["resources"]["primary_identifier"]
        == context.device_identifier
    ), (
        "The device primary identifier doesn't match, expected "
        + context.device_identifier
        + " current "
        + device_list_filtered["resources"]["primary_identifier"]
    )
    assert device_list_filtered["resources"]["gateway_id"] == context.gateway_id, (
        "The device gateway id doesn't match, expected "
        + context.gateway_id
        + " current "
        + device_list_filtered["resources"]["gateway_id"]
    )


@step("the user wants to get the list of vital ranges of the devices")
def get_device_vital_ranges_list(context):
    context.device_id = "00000000-0000-0000-0000-000000000001"
    url = "/web/device/" + context.device_id + "/range"
    context.response = requests_get(context, url)


@step("vital ranges list is received to verify device ranges")
def verify_device_information(context):
    device_vital_ranges_list = context.response.json()
    for index, payload_entry in enumerate(device_vital_ranges_list["resources"]):
        device_code_from_api = device_vital_ranges_list["resources"][index]["code"]
        if device_codes["HR"] == device_code_from_api:
            assert (
                device_vital_ranges_list["resources"][index]["upper_limit"] == "110.0"
            ), (
                "The device vital range doesn't match, expected "
                + "110.0"
                + " current "
                + device_vital_ranges_list["resources"][index]["upper_limit"]
            )
            assert (
                device_vital_ranges_list["resources"][index]["lower_limit"] == "50.0"
            ), (
                "The device vital range doesn't match, expected "
                + "50.0"
                + " current "
                + device_vital_ranges_list["resources"][index]["lower_limit"]
            )
        if device_codes["RR"] == device_code_from_api:
            assert (
                device_vital_ranges_list["resources"][index]["upper_limit"] == "160.0"
            ), (
                "The device vital range doesn't match, expected "
                + "160.0"
                + " current "
                + device_vital_ranges_list["resources"][index]["upper_limit"]
            )
            assert (
                device_vital_ranges_list["resources"][index]["lower_limit"] == "90.0"
            ), (
                "The device vital range doesn't match, expected "
                + "90.0"
                + " current "
                + device_vital_ranges_list["resources"][index]["lower_limit"]
            )
        if device_codes["SYS"] == device_code_from_api:
            assert (
                device_vital_ranges_list["resources"][index]["upper_limit"] == "120.0"
            ), (
                "The device vital range doesn't match, expected "
                + "120.0"
                + " current "
                + device_vital_ranges_list["resources"][index]["upper_limit"]
            )
            assert (
                device_vital_ranges_list["resources"][index]["lower_limit"] == "45.0"
            ), (
                "The device vital range doesn't match, expected "
                + "45.0"
                + " current "
                + device_vital_ranges_list["resources"][index]["lower_limit"]
            )
        if device_codes["DIA"] == device_code_from_api:
            assert (
                device_vital_ranges_list["resources"][index]["upper_limit"] == "102.02"
            ), (
                "The device vital range doesn't match, expected "
                + "102.02"
                + " current "
                + device_vital_ranges_list["resources"][index]["upper_limit"]
            )
            assert (
                device_vital_ranges_list["resources"][index]["lower_limit"] == "93.2"
            ), (
                "The device vital range doesn't match, expected "
                + "93.2"
                + " current "
                + device_vital_ranges_list["resources"][index]["lower_limit"]
            )
        if device_codes["SPO2"] == device_code_from_api:
            assert (
                device_vital_ranges_list["resources"][index]["upper_limit"] == "100.0"
            ), (
                "The device vital range doesn't match, expected "
                + "100.0"
                + " current "
                + device_vital_ranges_list["resources"][index]["upper_limit"]
            )
            assert (
                device_vital_ranges_list["resources"][index]["lower_limit"] == "85.0"
            ), (
                "The device vital range doesn't match, expected "
                + "85.0"
                + " current "
                + device_vital_ranges_list["resources"][index]["lower_limit"]
            )
        if device_codes["PR"] == device_code_from_api:
            assert (
                device_vital_ranges_list["resources"][index]["upper_limit"] == "120.0"
            ), (
                "The device vital range doesn't match, expected "
                + "120.0"
                + " current "
                + device_vital_ranges_list["resources"][index]["upper_limit"]
            )
            assert (
                device_vital_ranges_list["resources"][index]["lower_limit"] == "45.0"
            ), (
                "The device vital range doesn't match, expected "
                + "45.0"
                + " current "
                + device_vital_ranges_list["resources"][index]["lower_limit"]
            )
        if device_codes["TEMPERATURE_SKIN"] == device_code_from_api:
            assert (
                device_vital_ranges_list["resources"][index]["upper_limit"] == "0.0"
            ), (
                "The device vital range doesn't match, expected "
                + "0.0"
                + " current "
                + device_vital_ranges_list["resources"][index]["upper_limit"]
            )
            assert (
                device_vital_ranges_list["resources"][index]["lower_limit"] == "None"
            ), (
                "The device vital range doesn't match, expected "
                + "None"
                + " current "
                + device_vital_ranges_list["resources"][index]["lower_limit"]
            )
        if device_codes["TEMPERATURE_BODY"] == device_code_from_api:
            assert (
                device_vital_ranges_list["resources"][index]["upper_limit"] == "120.0"
            ), (
                "The device vital range doesn't match, expected "
                + "120.0"
                + " current "
                + device_vital_ranges_list["resources"][index]["upper_limit"]
            )
            assert (
                device_vital_ranges_list["resources"][index]["lower_limit"] == "None"
            ), (
                "The device vital range doesn't match, expected "
                + "None"
                + " current "
                + device_vital_ranges_list["resources"][index]["lower_limit"]
            )
        if device_codes["FALLS"] == device_code_from_api:
            assert (
                device_vital_ranges_list["resources"][index]["upper_limit"] == "30.0"
            ), (
                "The device vital range doesn't match, expected "
                + "30.0"
                + " current "
                + device_vital_ranges_list["resources"][index]["upper_limit"]
            )
            assert (
                device_vital_ranges_list["resources"][index]["lower_limit"] == "5.0"
            ), (
                "The device vital range doesn't match, expected "
                + "5.0"
                + " current "
                + device_vital_ranges_list["resources"][index]["lower_limit"]
            )
        if device_codes["POSITION_DURATION"] == device_code_from_api:
            assert (
                device_vital_ranges_list["resources"][index]["upper_limit"] == "102.2"
            ), (
                "The device vital range doesn't match, expected "
                + "102.2"
                + " current "
                + device_vital_ranges_list["resources"][index]["upper_limit"]
            )
            assert (
                device_vital_ranges_list["resources"][index]["lower_limit"] == "93.2"
            ), (
                "The device vital range doesn't match, expected "
                + "93.2"
                + " current "
                + device_vital_ranges_list["resources"][index]["lower_limit"]
            )


@step("the device and the bed exist")
def bed_device_exist(context):
    if context.env_config["environment"].upper() == "QA":
        context.bed_id = "73c207df-61ad-4a3c-b429-3a393a8e351e"
        context.device_uuid = "00000000-0000-0000-0000-000000000000"
    elif context.env_config["environment"].upper() == "PROD":
        context.bed_id = "b7aee215-a6dc-4a1c-b4b7-e742e6ed67ec"
        context.device_uuid = "00000000-0000-0000-0000-000000000001"


@step("Tom assigns a Patient Monitor to a bed")
def assign_pm_bed(context):
    context.execute_steps(
        """ 
           Given A request to assign bed to a device through Tucana's API
           When the request is made to assign bed to a device
           Then the user is told the request to assign bed to a device was successful
        """
    )
