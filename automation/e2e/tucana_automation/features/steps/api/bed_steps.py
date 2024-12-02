import json
import logging
import time
import uuid

from behave import *
from faker import Faker

from features.pages.bed_management_page import BedManagementPage
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


@step("A request to create a new bed through Tucana's API")
@step('a request to create a bed with invalid name "{name}" in payload')
def create_bed(context, name="true"):
    faker = Faker()
    if name == "true":
        context.bed_name = faker.bothify("ABQA ##-###")
        logging.info(f'Random name to create the Bed: {context.bed_name}')
    else:
        context.bed_name = name
    context.data = {
        "url": "/web/bed/batch",
        "json": {"resources": [{"name": context.bed_name}]},
    }


@step("the request is made to create a bed")
def send_new_bed_request(context):
    url = context.data["url"]
    context.response = requests_post(context, url, context.data["json"], headers=None)


@step("the bed is created")
def verify_bed_created(context):
    bed_created = context.response.json()
    context.bed_id = bed_created["resources"][0]["id"]
    assert bed_created["resources"][0]["name"] == context.bed_name, (
        "The bed name doesn't match, expected "
        + context.bed_name
        + " current "
        + bed_created["resources"][0]["name"]
    )
    assert (
        "patient" in bed_created["resources"][0]
    ), "The patient field is not present in response"


@step("The bed is removed to keep the application clean")
def remove_bed_clean_application(context):
    context.data = {"url": "/web/bed/batch", "json": {"bed_ids": [context.bed_id]}}
    url = context.data["url"]
    context.response = requests_delete_batch(
        context, url, context.data["json"], headers=None
    )
    verify_delete_request_status(context)


@step("A request to create beds through Tucana's API")
def create_bed(context):
    faker = Faker()
    context.beds = []
    create_beds = 3
    for i in range(create_beds):
        beds_data = faker.bothify("ABQA ##-###")
        context.beds.append(beds_data)
    context.data = {
        "url": "/web/bed/batch",
        "json": {
            "resources": [
                {"name": context.beds[0]},
                {"name": context.beds[1]},
                {"name": context.beds[2]},
            ]
        },
    }


@step("the beds were created")
def verify_beds_created(context):
    context.beds_created = context.response.json()
    context.bed_name_and_id = {}
    for index, payload_entry in enumerate(context.beds_created["resources"]):
        context.bed_ids.append(context.beds_created["resources"][index]["id"])
        context.bed_name_and_id[context.beds[index]] = context.beds_created["resources"][index]["id"]
        assert (
            context.beds_created["resources"][index]["name"] == context.beds[index]
        ), (
            "The bed name doesn't match, expected "
            + context.beds[index]
            + " current "
            + context.beds_created["resources"][index]["name"]
        )
        assert (
            "patient" in context.beds_created["resources"][index]
        ), "The patient field is not present in response"


@step("some beds exist")
def some_beds_exist(context):
    context.execute_steps(
        """ 
            Given A request to create beds through Tucana's API
            When the request is made to create a bed
            Then the user is told the request to create was successful
            And the beds were created
        """
    )


@step("the user wants to get the list of beds")
def get_beds_list(context):
    url = "/web/bed"
    context.response = requests_get(context, url)


@step("beds list is received")
def verify_beds_list(context):
    context.beds_list = context.response.json()
    beds_created = context.beds_created
    context.beds_ids = []
    for index, payload_entry in enumerate(context.beds_list["resources"]):
        for index1, payload in enumerate(beds_created["resources"]):
            payload_beds_id = context.beds_list["resources"][index]["id"]
            existing_beds_id = beds_created["resources"][index1]["id"]
            if existing_beds_id == payload_beds_id:
                context.beds_ids.append(existing_beds_id)
                assert (
                    context.beds_list["resources"][index]["name"]
                    == beds_created["resources"][index1]["name"]
                ), (
                    "The bed name doesn't match, expected "
                    + beds_created["resources"][index1]["name"]
                    + " current "
                    + context.beds_list["resources"][index]["name"]
                )
                assert (
                    "patient" in context.beds_list["resources"][index1]
                ), "The patient field is not present in response"


@step("the beds list is received")
def verify_beds_list(context):
    context.beds_list = context.response.json()


@step("the request is made to create a bed through upsert endpoint")
@step("the request is made to update a bed through upsert endpoint")
@step("the request is made to assign bed to a device")
def send_new_request(context):
    url = context.data["url"]
    context.response = requests_put(context, url, context.data["json"], headers=None)


@step("A request to create a new bed through upsert endpoint")
def create_bed(context):
    faker = Faker()
    context.bed_id = str(uuid.uuid1())
    context.bed_name = faker.bothify("ABQA ##-###")
    context.data = {
        "url": "/web/bed/batch",
        "json": {"resources": [{"name": context.bed_name, "id": context.bed_id}]},
    }


@step("the user verifies that all the bed information is correct")
def verify_bed_information(context):
    beds_list = context.response.json()
    for index, payload_entry in enumerate(beds_list["resources"]):
        payload_beds_id = beds_list["resources"][index]["id"]
        if context.bed_id == payload_beds_id:
            assert beds_list["resources"][index]["name"] == context.bed_name, (
                "The bed name doesn't match, expected "
                + context.bed_name
                + " current "
                + beds_list["resources"][index]["name"]
            )


@step("the bed to update exists")
@step("the bed exists")
@step("a bed exists")
def bed_exist(context):
    context.execute_steps(
        """ 
            Given A request to create a new bed through upsert endpoint
            And authentication credentials are being included
            When the request is made to create a bed through upsert endpoint
            Then the user is told the request to create a new bed through upsert endpoint was successful
        """
    )


@step("A request to update a bed through upsert endpoint")
def update_bed(context):
    faker = Faker()
    context.bed_name = faker.bothify("ABQA ##-###")
    context.data = {
        "url": "/web/bed/batch",
        "json": {"resources": [{"name": context.bed_name, "id": context.bed_id}]},
    }


@step("A request to create six beds through Tucana's API")
def create_bed(context):
    faker = Faker()
    context.beds = []
    create_beds = 6
    for i in range(create_beds):
        beds_data = faker.bothify("ABQA ##-###")
        context.beds.append(beds_data)
    context.data = {
        "url": "/web/bed/batch",
        "json": {
            "resources": [
                {"name": context.beds[0]},
                {"name": context.beds[1]},
                {"name": context.beds[2]},
                {"name": context.beds[3]},
                {"name": context.beds[4]},
                {"name": context.beds[5]},
            ]
        },
    }


@step("A request to create {} beds through Tucana's API")
def create_multiple_beds(context, quantity):
    faker = Faker()
    context.beds = []
    resources = []

    for i in range(int(quantity)):
        bed_data = faker.unique.bothify("MABQA-###-####")
        context.beds.append(bed_data)
        resources.append({"name": bed_data})

    context.data = {"url": "/web/bed/batch",
                    "json": {"resources": resources}}

    context.execute_steps(
        """ 
            When the request is made to create a bed
            Then the user is told the request to create was successful
            And the beds were created
        """
    )


@step("several beds exist")
def several_beds_exist(context):
    context.execute_steps(
        """ 
            Given A request to create six beds through Tucana's API
            When the request is made to create a bed
            Then the user is told the request to create was successful
            And the beds were created
        """
    )


@step("all beds are removed to keep the application clean")
@step("The beds are removed to keep the application clean")
def remove_all_beds_clean_application(context):
    valid_user_credentials(context)
    context.data = {
        "url": "/web/bed/batch",
        "json": {
            "bed_ids": context.bed_ids
        },
    }
    url = context.data["url"]
    context.response = requests_delete_batch(
        context, url, context.data["json"], headers=None
    )
    verify_delete_request_status(context)

    if len(context.bed_ids) > 0:
        for i in context.bed_ids.copy():
            context.bed_ids.remove(i)


@step('Tom clicks on the "{}" button')
def back_to_step_one(context, button):
    bed_page = BedManagementPage(context.browser.driver)
    bed_page.back_to_step_one()


@step("Tom sees the Bed list quantity and names already obtained by API")
def verify_bed_qty_and_names(context):
    bed_page = BedManagementPage(context.browser.driver)
    assert bed_page.verify_beds_qty_and_names(context.beds_list), "Something went wrong comparing the bed qty and names"


@step('Tom completes the {} beds limits')
def completes_limit(context, beds_limit):
    bed_page = BedManagementPage(context.browser.driver)
    context.beds_names_created = bed_page.complete_beds_list(int(beds_limit))


@step("Tom wants to create one bed more and see the Bed Limit Reached popup")
def adding_new_see_popup(context):
    bed_page = BedManagementPage(context.browser.driver)
    bed_page.add_new_bed()
    assert bed_page.is_bed_limit_popup_present(), "The Bed Limit Popup was not here"


@step("Tom closes the Bed Limit popup")
def close_bed_limit_popup(context):
    bed_page = BedManagementPage(context.browser.driver)
    bed_page.close_bed_limit_popup()


@step("Tom deletes all created beds")
def deletes_all_created_beds(context):
    bed_page = BedManagementPage(context.browser.driver)
    bed_page.delete_all_created_beds(context.beds_names_created)
