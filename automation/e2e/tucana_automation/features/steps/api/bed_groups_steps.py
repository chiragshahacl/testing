import json
import time
import uuid

import faker
from behave import *
from faker import Faker

from features.pages.group_management_page import GroupManagementPage
from features.steps.api.bed_steps import bed_exist
from features.steps.api.common_api_steps import (
    valid_user_credentials,
    verify_delete_request_status,
)
from utils.api_utils import (
    requests_delete,
    requests_delete_batch,
    requests_get,
    requests_post,
    requests_put,
)


@step("A request to create bed groups through Tucana's API")
@step('a request to create bed groups with invalid name "{name}" in payload')
def create_bed_groups(context, name="true"):
    faker = Faker()
    context.bed_groups = []
    create_bed_groups = 3
    for i in range(create_bed_groups):
        if name == "true":
            context.bed_groups_name = faker.bothify("AGQA #####")
        else:
            context.bed_groups_name = name
        context.bed_groups_description = faker.sentence(nb_words=5)
        bed_groups_data = {
            "name": context.bed_groups_name,
            "description": context.bed_groups_description,
        }
        context.bed_groups.append(bed_groups_data)
    context.data = {
        "url": "/web/bed-group/batch",
        "json": {
            "resources": [
                context.bed_groups[0],
                context.bed_groups[1],
                context.bed_groups[2],
            ]
        },
    }


@step("the request is made to create bed groups")
def send_new_bed_groups_request(context):
    url = context.data["url"]
    context.response = requests_post(context, url, context.data["json"], headers=None)


@step("bed groups were created")
def verify_beds_groups_created(context):
    beds_groups_created = context.response.json()
    context.beds_groups_ids = []
    for index, payload_entry in enumerate(beds_groups_created["resources"]):
        context.beds_groups_ids.append(beds_groups_created["resources"][index]["id"])
        assert (
                beds_groups_created["resources"][index]["name"]
                == context.bed_groups[index]["name"]
        ), (
                "The bed groups name doesn't match, expected "
                + context.bed_groups[index]["name"]
                + " current "
                + beds_groups_created["resources"][index]["name"]
        )
        assert (
                beds_groups_created["resources"][index]["description"]
                == context.bed_groups[index]["description"]
        ), (
                "The bed groups description doesn't match, expected "
                + context.bed_groups[index]["description"]
                + " current "
                + beds_groups_created["resources"][index]["description"]
        )
        assert (
                "id" in beds_groups_created["resources"][index]
        ), "The id field is not present in response"
        assert (
                "beds" in beds_groups_created["resources"][index]
        ), "The beds field is not present in response"


@step("bed groups are removed to keep the application clean")
def remove_beds_groups_clean_application(context):
    context.data = {
        "url": "/web/bed-group/batch",
        "json": {
            "group_ids": context.beds_groups_ids
        }
    }
    url = context.data["url"]
    context.response = requests_delete_batch(
        context, url, context.data["json"], headers=None
    )
    verify_delete_request_status(context)


@step("the user wants to get the list of the bed groups")
def get_bed_groups_list(context):
    url = "/web/bed-group"
    context.response = requests_get(context, url)


@step("bed group list is received")
def verify_beds_groups_list(context):
    beds_groups_list = context.response.json()
    context.beds_groups_ids = []
    for index, payload_entry in enumerate(beds_groups_list["resources"]):
        for index1, payload in enumerate(context.bed_groups):
            existing_beds_group_name = context.bed_groups[index1]["name"]
            payload_beds_group_name = beds_groups_list["resources"][index]["name"]
            if existing_beds_group_name == payload_beds_group_name:
                context.beds_groups_ids.append(
                    beds_groups_list["resources"][index]["id"]
                )
                assert (
                        beds_groups_list["resources"][index]["description"]
                        == context.bed_groups[index1]["description"]
                ), (
                        "The bed groups description doesn't match, expected "
                        + context.bed_groups[index1]["description"]
                        + " current "
                        + beds_groups_list["resources"][index]["description"]
                )
                assert (
                        "id" in beds_groups_list["resources"][index]
                ), "The id field is not present in response"
                assert (
                        "beds" in beds_groups_list["resources"][index]
                ), "The beds field is not present in response"


@step("some bed groups exist")
def some_bed_groups_exist(context):
    context.execute_steps(
        """ 
            Given A request to create bed groups through Tucana's API
            When the request is made to create bed groups
            Then the user is told the request to create was successful
            And bed groups were created
        """
    )


@step("A request to create a new bed group through upsert endpoint")
def create_bed_group(context):
    faker = Faker()
    context.bed_group_id = str(uuid.uuid1())
    context.bed_group_name = faker.bothify("AGQA #####")
    context.bed_group_description = faker.sentence(nb_words=5)
    context.data = {
        "url": "/web/bed-group/batch",
        "json": {
            "resources": [
                {
                    "id": context.bed_group_id,
                    "name": context.bed_group_name,
                    "description": context.bed_group_description,
                },
            ]
        },
    }


@step("the request is made to create a bed group through upsert endpoint")
@step("the request is made to update a bed group through upsert endpoint")
def send_new_bed_group_request(context):
    url = context.data["url"]
    context.response = requests_put(context, url, context.data["json"], headers=None)


@step("the user verifies that all the bed group information is correct")
def verify_beds_groups_information(context):
    beds_groups_list = context.response.json()
    for index, payload_entry in enumerate(beds_groups_list["resources"]):
        payload_beds_group_id = beds_groups_list["resources"][index]["id"]
        if context.bed_group_id == payload_beds_group_id:
            assert (
                    beds_groups_list["resources"][index]["description"]
                    == context.bed_group_description
            ), (
                    "The bed groups description doesn't match, expected "
                    + context.bed_group_description
                    + " current "
                    + beds_groups_list["resources"][index]["description"]
            )
            assert (
                    beds_groups_list["resources"][index]["name"] == context.bed_group_name
            ), (
                    "The bed groups name doesn't match, expected "
                    + context.bed_group_name
                    + " current "
                    + beds_groups_list["resources"][index]["name"]
            )
            assert (
                    "beds" in beds_groups_list["resources"][index]
            ), "The beds field is not present in response"


@step("The bed group is removed to keep the application clean")
def remove_bed_group_clean_application(context):
    valid_user_credentials(context)
    context.data = {
        "url": "/web/bed-group/batch",
        "json": {"group_ids": [context.bed_group_id]},
    }
    url = context.data["url"]
    context.response = requests_delete_batch(
        context, url, context.data["json"], headers=None
    )
    verify_delete_request_status(context)


@step("the bed group to update exists")
@step("the bed group exists")
def bed_group_exist(context):
    context.execute_steps(
        """ 
            Given A request to create a new bed group through upsert endpoint
            And authentication credentials are being included
            When the request is made to create a bed group through upsert endpoint
            Then the user is told the request to create a new bed group through upsert endpoint was successful
        """
    )


@step("the bed group and some beds exists")
def bed_group_exist(context):
    context.execute_steps(
        """ 
            Given A request to create a new bed group through upsert endpoint
        """
    )



@step("A request to update a bed group through upsert endpoint")
def create_bed_group(context):
    faker = Faker()
    context.bed_group_name = faker.bothify("AGQA #####")
    context.bed_group_description = faker.sentence(nb_words=5)
    context.data = {
        "url": "/web/bed-group/batch",
        "json": {
            "resources": [
                {
                    "id": context.bed_group_id,
                    "name": context.bed_group_name,
                    "description": context.bed_group_description,
                },
            ]
        },
    }


@step("A request to assign beds to a Group")
def create_bed_group(context):
    context.data = {
        "json": {
            "bed_ids": context.bed_ids
        },
    }


@step("the request is made to assign beds to a Group")
def assign_bed_group_request(context):
    url = "web/bed-group/" + context.bed_group_id + "/beds"
    context.response = requests_put(context, url, context.data["json"], headers=None)


@step("the request is made to assign beds to a Group with invalid payload")
def assign_bed_group_request(context):
    context.data = {
        "json": {
            "resources": [
                {"name": "WRONG"},
                {"name": "BED"},
                {"name": "NAME"},
            ]
        },
    }
    url = "web/bed-group/" + context.bed_group_id + "/beds"
    context.response = requests_put(context, url, context.data["json"], headers=None)


@step("bed group list is received in order to verify the beds to a Group")
def verify_beds_groups_information(context):
    beds_groups_list = context.response.json()
    for index, payload_entry in enumerate(beds_groups_list["resources"]):
        payload_beds_group_id = beds_groups_list["resources"][index]["id"]
        if context.bed_group_id == payload_beds_group_id:
            assert (
                    beds_groups_list["resources"][index]["description"]
                    == context.bed_group_description
            ), (
                    "The bed groups description doesn't match, expected "
                    + context.bed_group_description
                    + " current "
                    + beds_groups_list["resources"][index]["description"]
            )
            assert (
                    beds_groups_list["resources"][index]["name"] == context.bed_group_name
            ), (
                    "The bed groups name doesn't match, expected "
                    + context.bed_group_name
                    + " current "
                    + beds_groups_list["resources"][index]["name"]
            )
            assert (
                    "beds" in beds_groups_list["resources"][index]
            ), "The beds field is not present in response"
            for index1, payload in enumerate(context.bed_ids):
                assert (
                        beds_groups_list["resources"][index]["beds"][index1]["id"]
                        == context.bed_ids[index1]
                ), (
                        "The bed doesn't match, expected"
                        + context.bed_ids[index1]
                        + " current "
                        + beds_groups_list["resources"][index]["beds"][index1]["id"]
                )


@step("A request to assign beds to a Groups")
def create_beds_groups(context):
    context.data = {
        "json": {
            "resources": [
                {
                    "group_id": context.beds_groups_ids[0],
                    "bed_ids": [context.bed_ids[0], context.bed_ids[1]],
                },
                {
                    "group_id": context.beds_groups_ids[1],
                    "bed_ids": [context.bed_ids[2], context.bed_ids[3]],
                },
                {
                    "group_id": context.beds_groups_ids[2],
                    "bed_ids": [context.bed_ids[4], context.bed_ids[5]],
                },
            ]
        }
    }


@step("the request is made to assign beds to a Groups")
def assign_beds_groups_request(context):
    url = "web/bed-group/beds/batch"
    context.response = requests_put(context, url, context.data["json"], headers=None)


@step("all bed group list are received in order to verify the beds to a Groups")
def verify_beds_groups_information(context):
    beds_groups_list = context.response.json()
    for index, payload_entry in enumerate(beds_groups_list["resources"]):
        for index0, payload_entrys in enumerate(context.beds_groups_ids):
            payload_beds_group_id = beds_groups_list["resources"][index]["id"]
            created_beds_groups_id = context.beds_groups_ids[index0]
            if created_beds_groups_id == payload_beds_group_id:
                assert (
                        beds_groups_list["resources"][index]["description"]
                        == context.bed_groups[index0]["description"]
                ), (
                        "The bed groups description doesn't match, expected "
                        + context.bed_groups[index0]["description"]
                        + " current "
                        + beds_groups_list["resources"][index]["description"]
                )
                assert (
                        beds_groups_list["resources"][index]["name"]
                        == context.bed_groups[index0]["name"]
                ), (
                        "The bed groups name doesn't match, expected "
                        + context.bed_groups[index0]["name"]
                        + " current "
                        + beds_groups_list["resources"][index]["name"]
                )
                assert (
                        "beds" in beds_groups_list["resources"][index]
                ), "The beds field is not present in response"
                for index1, payload2 in enumerate(context.beds_created):
                    for index2, payloads in enumerate(
                            beds_groups_list["resources"][index]["beds"]
                    ):
                        if (
                                context.beds_created["resources"][index1]["id"]
                                == beds_groups_list["resources"][index]["beds"][index2][
                            "id"
                        ]
                        ):
                            assert (
                                    beds_groups_list["resources"][index]["beds"][index2][
                                        "name"
                                    ]
                                    == context.beds_created["resources"][index1]["name"]
                            ), (
                                    "The bed name doesn't match, expected"
                                    + context.beds_created["resources"][index1]["name"]
                                    + " current "
                                    + beds_groups_list["resources"][index]["beds"][index2][
                                        "name"
                                    ]
                            )


@step("the user wants to get the bed group observations")
def assign_bed_group_request(context):
    context.bed_group_id = "7c2a852e-2ee2-41b0-aff3-0b89c1fb84ff"
    url = "web/bed-group/" + context.bed_group_id + "/alerts"
    context.response = requests_get(context, url)


@step("bed group observations is received")
def verify_beds_groups_observations(context):
    beds_groups_observations = context.response.json()
    for index, payload_entry in enumerate(beds_groups_observations["resources"]):
        for index1, payload in enumerate(context.bed_groups):
            patient_id_listed = context.bed_groups["resources"][index]["patientId"]
            payload_beds_group_name = beds_groups_observations["resources"][index][
                "name"
            ]
            if context.patient_id == patient_id_listed:
                context.beds_groups_ids.append(
                    beds_groups_observations["resources"][index]["id"]
                )
                assert (
                        beds_groups_observations["resources"][index]["description"]
                        == context.bed_groups[index1]["description"]
                ), (
                        "The bed groups description doesn't match, expected "
                        + context.bed_groups[index1]["description"]
                        + " current "
                        + beds_groups_observations["resources"][index]["description"]
                )
                assert (
                        "id" in beds_groups_observations["resources"][index]
                ), "The id field is not present in response"
                assert (
                        "beds" in beds_groups_observations["resources"][index]
                ), "The beds field is not present in response"


@step("the bed is assigned to the group")
def assign_bed_group(context):
    context.execute_steps(
        """ 
            Given A request to assign bed to a Group
            And authentication credentials are being included
            When the request is made to assign beds to a Groups
            Then the user is told the request to assign was successful
        """
    )


@step("A request to assign bed to a Group")
def assign_bed_group(context):
    context.data = {
        "json": {
            "resources": [
                {
                    "group_id": context.bed_group_id,
                    "bed_ids": [context.bed_id],
                }
            ]
        }
    }


@step("The beds are assigned to the group")
def assign_beds_to_a_group(context):
    context.execute_steps(
        """ 
            Given authentication credentials are being included
            And A request to assign the created beds to the Group
            Then the user is told the request to assign was successful
        """
    )


@step("A request to assign the created beds to the Group")
def create_bed_group(context):
    url = "web/bed-group/beds/batch"
    context.data = {
        "json": {
            "resources": [
                {
                    "group_id": context.bed_group_id,
                    "bed_ids": context.bed_ids
                }
            ]
        }
    }
    context.response = requests_put(context, url, context.data["json"], headers=None)


@step("Tom assures there's at least {} beds created")
def verify_at_least_twenty_beds(context, bed_limit):
    url = "/web/bed"
    context.response = requests_get(context, url, headers=None)
    assert context.response.status_code == 200, f"Expected status code 200, current {context.response.status_code}"
    jsonify_response = json.loads(context.response.text)
    context.current_bed_qty = len(jsonify_response['resources'])
    context.bed_ids = []
    if len(jsonify_response['resources']) < int(bed_limit):
        for i in range(int(bed_limit) - context.current_bed_qty):
            bed_exist(context)
            context.bed_ids.append(context.bed_id)


@step("Tom selects {} beds")
def selects_x_beds(context, total_beds):
    group_management_page = GroupManagementPage(context.browser.driver)
    group_management_page.select_beds(int(total_beds))


@step("Tom tries to select one more but it should be not possible")
def select_one_bed_more(context):
    group_management_page = GroupManagementPage(context.browser.driver)
    assert group_management_page.check_checkbox_disabled(), "The Bed checkboxs should be disabled and it is not"


@step("Tom wants to get bed group observations")
def get_bed_group_observations(context):
    url = "/web/bed-group/" + context.patient_bed_and_group["group"] + "/alerts"
    context.response = requests_get(context, url)


@step("Tom verifies that the bed group observations information is correct")
def verify_bed_group_observations(context):
    bed_group_alerts_response = context.response.json()
    assert bed_group_alerts_response["resources"][0]["code"] == context.alarm_code, (
            "Expected alarm code "
            + bed_group_alerts_response["resources"][0]["code"]
            + " current "
            + context.alarm_code
    )
    assert bed_group_alerts_response["resources"][0]["deviceCode"] == context.device_code, (
            "Expected device code "
            + bed_group_alerts_response["resources"][0]["deviceCode"]
            + " current "
            + context.device_code
    )
    assert bed_group_alerts_response["resources"][0]["devicePrimaryIdentifier"] == context.sensor_type, (
            "Expected device primary identifier "
            + bed_group_alerts_response["resources"][0]["devicePrimaryIdentifier"]
            + " current "
            + context.sensor_type
    )
    assert bed_group_alerts_response["resources"][0]["valueText"] == context.priority, (
            "Expected priority "
            + bed_group_alerts_response["resources"][0]["valueText"]
            + " current "
            + context.priority
    )