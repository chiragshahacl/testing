import logging
import time

from behave import *

from features.pages.dashboard_page import DashboardPage
from features.pages.group_management_page import GroupManagementPage


@step("Tom wants to create a new group")
def create_new_group(context):
    assert (
        context.current_page.is_new_group_sign_present()
    ), "Can not find the Add new group sign"


@step("Tom clicks on the add a new group sign")
@step("Tom sees the current group number and clicks on the add a new group sign")
def group_add(context):
    context.current_groups = context.current_page.get_groups_qty()
    context.current_page.create_new_group()
    context.new_listed_groups = context.current_page.listed_groups()


@step("Tom sees the new group listed")
@step("Tom sees the new group listed and the group quantity increased")
def sees_new_group(context):
    expected_qty = context.current_groups + 1
    assert context.current_page.get_groups_qty() == expected_qty, (
        "Expected Groups Quantity "
        + str(expected_qty)
        + " current "
        + context.current_page.get_groups_qty()
    )


@step("Tom sees the default group name was set correctly")
def default_group_name(context):
    context.new_group_name = context.current_page.get_default_group_name(
        str(context.current_groups + 1)
    )
    assert (
        "Group" in context.new_group_name
    ), "New Default Group should have the 'Group' word in it, and it has not"
    context.group_name = context.new_group_name


@step("Tom deletes the default group added")
def delete_default_group(context):
    context.current_page = GroupManagementPage(context.browser.driver)
    context.current_page.delete_group(context.group_name)


@step('Tom deletes the "{}" added')
def delete_group_added(context, group_name):
    context.current_page = GroupManagementPage(context.browser.driver)
    context.current_page.delete_group(group_name)


@step("Tom should not see the last group added anymore")
@step("Tom should not see the named group anymore")
def group_deleted(context):
    time.sleep(5)
    context.current_page = DashboardPage(context.browser.driver)
    assert not context.current_page.is_new_group_in_dashboard(
        context.group_name
    ), "Group still present"


@step("Tom adds two random beds to the group")
def add_two_random_beds(context):
    context.selected_beds = []
    first_bed_name, first_bed_uid = context.current_page.select_one_bed()
    for i in range(6):
        if first_bed_name is None:
            first_bed_name, first_bed_uid = context.current_page.select_one_bed()
        else:
            break

    second_bed_name, second_bed_uid = context.current_page.select_one_bed(
        first_bed_name
    )
    for i in range(4):
        if second_bed_name is None:
            second_bed_name, second_bed_uid = context.current_page.select_one_bed(
                first_bed_name
            )
        else:
            break
    context.selected_beds.append([first_bed_name, first_bed_uid])
    context.selected_beds.append([second_bed_name, second_bed_uid])


@step("Tom sees the two random beds added to the group")
def verify_added_beds(context):
    for index, bed in enumerate(context.selected_beds):
        assert context.current_page.is_bed_listed(bed, str(index + 1)), (
            "The bed " + bed[0] + " is not listed"
        )


@step("Tom sees the finish setup button disabled")
def finish_setup_disabled(context):
    assert (
        context.current_page.is_finish_setup_disabled()
    ), "The finish setup button was enabled and it should not"


@step("Tom sees the finish setup button enabled")
def finish_setup_enabled(context):
    assert (
        context.current_page.is_finish_setup_enabled()
    ), "The finish setup button was disabled and it should not"


@step("Tom clicks on the finish setup button")
def click_finish_setup(context):
    context.current_page.finish_setup()


@step("Tom clicks on confirm setup button")
def confirm_setup(context):
    context.current_page.click_on_confirm()


@step("Tom is redirected to the home dashboard")
def redirect_home(context):
    context.current_page = DashboardPage(context.browser.driver)
    time.sleep(5)
    assert (
        context.current_page.get_current_url() == context.env_config["app_url"] + "home"
    ), "The user was not redirected"


@step("Tom sees the new group and the beds displayed in the dashboard")
def group_in_dashboard(context):
    group_page = GroupManagementPage(context.browser.driver)
    group_page.wait_until_confirm_is_gone()
    time.sleep(5)
    context.current_page = DashboardPage(context.browser.driver)
    assert context.current_page.is_new_group_in_dashboard(
        context.group_name
    ), "Something went wrong getting the new group name"
    context.current_page.click_group_in_dashboard(context.group_name)
    time.sleep(3)
    for bed in context.selected_beds:
        assert context.current_page.is_bed_in_groups(
            bed[0]
        ), "Something went wrong getting the bed name inside the dashboard"


@step("Tom wants to edit the group name with a random name")
@step('Tom wants to edit the group name with the name "{}"')
def edit_name_w_spaces(context, group_name=None):
    context.old_name = context.new_listed_groups[len(context.new_listed_groups) - 1]
    if group_name is None:
        from faker import Faker

        faker = Faker()
        group_name = faker.bothify("WGQA #####")
    context.group_name = group_name
    context.current_page.edit_group_name(group_name, context.old_name)


@step("Tom deletes the last group added")
def delete_specific_group(context):
    context.current_page = GroupManagementPage(context.browser.driver)
    context.current_page.delete_group(context.group_name)


@step("Tom should not see the group anymore")
def group_no_more(context):
    time.sleep(5)
    context.current_page = DashboardPage(context.browser.driver)
    assert not context.current_page.is_new_group_in_dashboard(
        context.group_name
    ), "The group {} is still present".format(context.group_name)


@step("Tom is able to navigate between groups and view assigned beds")
def navigate_all_groups(context):
    group_names = context.current_page.get_dashboard_groups()
    assert len(group_names) == len(
        context.group_and_beds.keys()
    ), "Groups qty in group management doesn't match with the dashboard ones"
    for group in context.group_and_beds.keys():
        context.current_page.click_group_in_dashboard(group)
        time.sleep(5)
        bed_names = context.current_page.get_bed_names()
        assert len(bed_names) == len(
            context.group_and_beds[group]
        ), "Bed qty in group management doesn't match with the dashboard ones"
        for bed in context.group_and_beds[group]:
            assert context.current_page.is_bed_in_groups(bed), (
                "Expected bed_name " + bed + " was not found"
            )


@step("Tom saves all groups and beds information")
def save_all_groups_and_beds(context):
    context.current_page = GroupManagementPage(context.browser.driver)
    context.group_and_beds = context.current_page.save_groups_and_beds()


@step("Tom closes the group management modal")
def close_group_management_modal(context):
    context.current_page.close_modal()


@step("Tom closes discard the changes")
def close_group_management_modal(context):
    context.current_page.discard_changes()


@step('Tom navigates to the group "{}"')
def navigate_to_group(context, group_name):
    context.current_page = DashboardPage(context.browser.driver)
    context.current_page.click_group_in_dashboard(group_name)


@step("Tom can see that the beds in a group displaying a complete patient information")
def see_beds_data(context):
    beds = context.current_page.get_beds_qty()
    time.sleep(10)
    for i in range(beds):
        bed_info = context.current_page.get_bed_info(i).split("\n")
        time.sleep(1)
        logging.info(bed_info)
        if not len(bed_info) >= 7:
            if "PATIENT MONITOR IS NOT AVAILABLE" in bed_info:
                logging.info("PATIENT MONITOR IS NOT AVAILABLE")
            else:
                assert (
                    len(bed_info) >= 7
                ), "Expected bed information, 7 or more elements, current " + str(
                    len(bed_info)
                )
        else:
            if "ECG LEAD-OFF" in bed_info:
                logging.info("PATIENT ECG LEAD-OFF")
            elif "NO ANNE CHEST SENSOR PAIRED" in bed_info:
                logging.info("NO ANNE CHEST SENSOR PAIRED")
            else:
                assert (
                    "ECG" in bed_info
                ), "Expected ECG information, but it was not found"
                assert (
                    "HR (bpm)" in bed_info
                ), "Expected value HR (bpm) but it was not found"


@step('Tom sees the error message "{}" displayed in group management popup')
def error_message_displayed(context, error_message):
    assert context.current_page.is_error_message_present(error_message)


@step("Tom sees the Bed Group created and clicks on it")
def click_on_group_created(context):
    context.current_page.click_group_in_dashboard(context.bed_group_name)


@step("Tom sees the Bed Group and the bed created and clicks on it")
def click_on_bed_group_and_bed(context):
    context.current_page.click_group_in_dashboard(context.bed_group_name)
    context.current_page.click_on_bed(context.bed_name)


@step('Tom sees the "{}" message in the dashboard')
def sees_message_dashboard(context, message):
    context.current_page = DashboardPage(context.browser.driver)
    click_on_group_created(context)
    assert context.current_page.is_message_present(message)


@step('Tom sees the "{}" message in the bed details')
def sees_message_bed_details(context, message):
    context.current_page = DashboardPage(context.browser.driver)
    # click_on_bed_group_and_bed(context)
    assert context.current_page.is_message_present(message)


@step("Tom sees a red outline around the field")
def verify_red_outline(context):
    assert context.current_page.verify_field_outline(context.old_name), 'Field should have a red outline around, but it has not'


@step("Tom deletes the predefined group name and leaves it empty")
def group_name_delete_leave_empty(context):
    context.old_name = context.new_listed_groups[len(context.new_listed_groups) - 1]
    context.current_page.edit_group_name("", context.old_name)


@step("Tom sees the existent groups names")
def get_existent_groups_names(context):
    group_management_page = GroupManagementPage(context.browser.driver)
    context.groups_names = group_management_page.get_groups_names()


@step("Tom sets one of the already existent group name")
def set_already_name(context):
    group_management_page = GroupManagementPage(context.browser.driver)
    context.old_name = context.new_listed_groups[len(context.new_listed_groups) - 1]
    group_management_page.edit_group_name(context.groups_names[0], context.old_name)


@step("Tom sees a message telling the name is already in use")
def group_name_inuse_message(context):
    group_management_page = GroupManagementPage(context.browser.driver)
    assert group_management_page.is_group_name_in_use(), "The 'Bed group name already exists. Change or enter a new one.' message wasn't present"


@step("Tom closes the Bed detail popup and he sees the Multi-Patient view again")
def closes_bed_details(context):
    context.current_page.close_bed_detail_modal()
    assert context.current_page.multi_patient_view_presence()
