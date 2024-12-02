import time

from behave import *
from faker import Faker

from features.pages.bed_detail_page import BedDetailPage
from features.pages.bed_management_page import BedManagementPage
from features.pages.dashboard_page import DashboardPage
from features.pages.group_management_page import GroupManagementPage
from features.steps.web.common_steps import clicks_on_dashboard_option
from features.steps.web.group_steps import click_on_bed_group_and_bed, click_on_group_created


@step("Tom wants to create a new bed")
def create_new_bed(context):
    context.current_beds_qty = context.current_page.back_to_step_one()
    context.current_beds_qty = context.current_page.get_bed_qty()
    assert context.current_page.is_add_new_bed_btn_available()


@step("Tom clicks on the add a new bed sign")
def add_new_bed(context):
    context.current_page.add_new_bed()
    context.new_beds_qty = context.current_page.get_bed_qty()
    assert context.new_beds_qty == context.current_beds_qty + 1, (
        "Expected quantity beds "
        + context.current_beds_qty
        + 1
        + " current "
        + context.new_beds_qty
    )


@step('Tom wants to edit the bed\'s name with the name "{}"')
@step("Tom wants to edit the bed's name with a random name")
@step('Tom sets the bed\'s name as "{}"')
def set_bed_name(context, bed_name=None):
    faker = Faker()
    if bed_name is None:
        bed_name = faker.bothify("BQA ##-###")
    context.bed_name = bed_name
    context.current_page.set_bed_name(context.new_beds_qty, bed_name)


@step("Tom sees the new bed listed")
@step("Tom sees the new bed listed at the bottom")
def bed_listed(context):
    assert context.bed_name == context.current_page.get_bed_name(
        context.new_beds_qty
    ), (
        "Expected bed name "
        + context.bed_name
        + " current "
        + context.current_page.get_bed_name(context.new_beds_qty)
    )


@step("Tom sees the edited name listed")
def bed_listed(context):
    assert context.bed_name == context.current_page.get_bed_name(
        context.new_beds_qty
    ), (
        "Expected bed name "
        + context.bed_name
        + " current "
        + context.current_page.get_bed_name(context.new_beds_qty)
    )


@step("Tom clicks on the next setup button")
def next_assign_bed_to_monitor(context):
    context.current_page.click_on_next()


@step("Tom sees the STEP 2 assignment page")
def bed_to_monitor_management(context):
    assert context.current_page.is_bed_management_present()


@step("Tom saves the bed assigned to the patient monitor")
def assign_bed_to_monitor(context):
    context.current_page.save_monitor_bed(context)


@step("Tom assigns the new bed to a patient")
def assign_bed_to_monitor(context):
    context.current_page.assign_monitor_to_bed(context.bed_name)


@step("Tom clicks on the finish bed setup button")
def click_finish_bed_setup(context):
    bed_page = BedManagementPage(context.browser.driver)
    context.current_page = bed_page
    bed_page.finish_setup()


@step("Tom clicks on confirm")
def confirm_bed_setup(context):
    context.current_page.confirm_bed_setup()


@step("Tom restores the bed assigned to the patient monitor")
def confirm_bed_setup(context):
    clicks_on_dashboard_option(context, "Bed Management")
    context.current_page = BedManagementPage(context.browser.driver)
    context.current_page.assign_monitor_to_bed(context.bed_id_monitor_one)


@step("Tom adds the created bed to the group")
def add_specific_bed(context):
    context.current_page = GroupManagementPage(context.browser.driver)
    time.sleep(2)
    context.current_page.select_specific_bed(context.bed_name)


@step("Tom sees the created bed added to the group")
def specific_bed_in_group(context):
    assert context.current_page.specific_bed_in_group(
        context.bed_name
    ), "Specific bed {}, was not found in group".format(context.bed_name)


@step("Tom sees the new group and the new bed displayed in the dashboard")
def sees_specific_bed_in_group(context):
    group_page = GroupManagementPage(context.browser.driver)
    group_page.wait_until_confirm_is_gone()
    time.sleep(5)
    context.current_page = DashboardPage(context.browser.driver)
    assert context.current_page.is_new_group_in_dashboard(
        context.group_name
    ), "Something went wrong getting the new group name"
    context.current_page.click_group_in_dashboard(context.group_name)
    time.sleep(3)
    assert context.current_page.is_bed_in_groups(
        context.bed_name
    ), "Something went wrong getting the bed name inside the dashboard"


@step("Tom deletes the created bed")
def bed_del(context):
    bed_page = BedManagementPage(context.browser.driver)
    bed_page.back_to_step_one()
    bed_page.delete_bed(context.bed_name)
    context.current_page = bed_page


@step("Tom should not see the bed anymore")
def verify_bed_listed(context):
    assert not context.current_page.bed_still_listed(
        context.bed_name
    ), "The bed {} is still listed".format(context.bed_name)


@step('Tom selects the "{}" bed')
def select_patient_bed(context, patient):
    context.current_page = DashboardPage(context.browser.driver)
    patient_bed = context.current_page.get_patient_bed_id(patient)
    context.current_page.select_patient_bed(patient)
    context.current_page = BedDetailPage(context.browser.driver)
    assert context.current_page.is_left_bed_info_completed(
        patient_bed
    ), "Can not get all the information from the left bed menu"


@step('Tom selects the "{}" tab')
def select_tab_inside_bed(context, tab_name):
    context.current_page = BedDetailPage(context.browser.driver)
    context.current_page.select_tab(tab_name)


@step(
    'Tom sees the ID "{}", First Name "{}", Last Name "{}", Sex "{}", DOB "{}" listed'
)
def see_patient_info_inside_tab(context, patient_id, first_name, last_name, sex, dob):
    time.sleep(5)
    assert (
        patient_id == context.current_page.get_patient_id()
    ), f"Expected patient ID {patient_id}, current {context.current_page.get_patient_id()}"
    assert (
        first_name == context.current_page.get_patient_first_name()
    ), f"Expected patient first name {first_name}, current {context.current_page.get_patient_first_name()}"
    assert (
        last_name == context.current_page.get_patient_last_name()
    ), f"Expected patient ID {last_name}, current {context.current_page.get_patient_last_name()}"
    assert (
        sex == context.current_page.get_patient_sex()
    ), f"Expected patient ID {sex}, current {context.current_page.get_patient_sex()}"
    assert (
        dob == context.current_page.get_patient_dob()
    ), f"Expected patient ID {dob}, current {context.current_page.get_patient_dob()}"


@step('Tom sees the Alarm Name "{}", Alarm "{}", Low Limit "{}", High Limit "{}"')
def see_alarms_limits_in_tabs(context, alarm_name, alarm, low_limit, high_limit):
    assert context.current_page.is_alarm_present(alarm_name, alarm)
    assert "Low limit " + low_limit == context.current_page.get_alarm_low_limit(
        alarm_name, alarm
    ), f"Expected Low Level Limit {low_limit}, current {context.current_page.get_alarm_low_limit(alarm_name, alarm)}"
    assert "High limit " + high_limit == context.current_page.get_alarm_high_limit(
        alarm_name, alarm
    ), f"Expected High Level Limit {high_limit}, current {context.current_page.get_alarm_high_limit(alarm_name, alarm)}"


@step('Tom sees the following Alarms Names and limits')
def see_alarms_limits_in_tabs(context):
    for row in context.table:
        assert context.current_page.is_alarm_present(row['Alarm'], row['Unit'])
        assert row['Low Limit'] == context.current_page.get_alarm_low_limit(row['Alarm']), f"Expected Low Level Limit {row['Low Limit']}, current {context.current_page.get_alarm_low_limit(row['Alarm'])}"
        assert row['High Limit'] == context.current_page.get_alarm_high_limit(row['Alarm']), f"Expected High Level Limit {row['High Limit']}, current {context.current_page.get_alarm_high_limit(row['Alarm'])}"


@step("Tom should see the following Patient's sensors with their correspondant icons")
def check_sensors_list(context):
    bed_detail_page = BedDetailPage(context.browser.driver)
    for row in context.table:
        bed_detail_page.verify_sensor_information(row["Sensor"], row["Sensor ID"])


@step("Tom assures the patient bed has a PM with sensors available")
def assign_pm_to_patient(context):
    if context.env_config["environment"].upper() == "QA":
        context.bed_id = "73c207df-61ad-4a3c-b429-3a393a8e351e"
        context.device_uuid = "00000000-0000-0000-0000-000000000000"
    elif context.env_config["environment"].upper() == "PROD":
        context.bed_id = "b7aee215-a6dc-4a1c-b4b7-e742e6ed67ec"
        context.device_uuid = "00000000-0000-0000-0000-000000000001"
    context.execute_steps(
        """ 
            Given A request to assign bed to a device through Tucana's API
            When the request is made to assign bed to a device
            Then the user is told the request to assign bed to a device was successful
        """
    )


@step('Tom sees the error message "{}" displayed in bed management popup')
def error_message_displayed(context, error_message):
    assert context.current_page.is_error_message_present(error_message)


@step("Tom clicks on the add a new bed with the same name")
def add_new_bed(context):
    context.current_page.add_new_bed()
    context.new_beds_qty = context.new_beds_qty + 1


@step("Tom sees the unsaved information popup")
def unsaved_information(context):
    assert context.current_page.is_unsaved_information_title_present()


@step("Tom sees the unsaved changes popup and closes it")
def unsaved_information_title_present(context):
    assert context.current_page.is_unsaved_changes_title_present()
    context.current_page.back_to_edit()


@step('Tom clicks on "{}" button')
def error_message_displayed(context, button_name):
    context.current_page.click_on_unsaved_information_button(button_name)


@step("Tom sees the confirmation required popup")
def confirmation_required_title_present(context):
    assert context.current_page.is_confirmation_required_title_present()


@step("Tom should see the following Patient's vitals information")
def check_sensors_list(context):
    bed_detail_page = BedDetailPage(context.browser.driver)
    for row in context.table:
        bed_detail_page.verify_vitals_information(row["Information"])


@step('Tom sees the "{}" message at the left card')
def sees_left_card_message(context, message):
    context.current_page = BedDetailPage(context.browser.driver)
    context.current_page = DashboardPage(context.browser.driver)
    # click_on_group_created(context)
    context.current_page = BedDetailPage(context.browser.driver)
    assert context.current_page.is_message_inside_left_card(message)


@step('Tom sees the "{}" and "{}" inside the left card')
def sees_left_card_data(context, data1, data2):
    context.current_page = DashboardPage(context.browser.driver)
    # click_on_group_created(context)
    bed_detail_page = BedDetailPage(context.browser.driver)
    assert bed_detail_page.is_data_inside_left_card(data1, data2)


@step('Tom sees the Patient Monitor "{}" ID inside the Web APP')
def sees_patient_monitor_web(context, identifier):
    bed_detail_page = BedDetailPage(context.browser.driver)
    assert bed_detail_page.is_pm_id_present(identifier), "Something went wrong matching PM ID inside the bed detail page"


@step("Tom verifies the current PM quantity inside the Bed Management Page should be {}")
def current_pm_qty_in_bm(context, limit):
    bed_management_page = BedManagementPage(context.browser.driver)
    current_pm_qty = bed_management_page.current_pm_qty()
    assert int(limit) == current_pm_qty, f"Expected PM in list {limit}, current {current_pm_qty}"


@step("Tom verifies the extra Patient Monitor is not listed")
def verify_pm_in_list(context):
    bed_management_page = BedManagementPage(context.browser.driver)
    assert not bed_management_page.is_pm_listed(context.pm_extra), f"{context.pm_extra} extra PM should not be listed and it is"


@step("Tom sees the alarm history is the expected one")
def alarm_history_verification(context):
    context.current_page = BedDetailPage(context.browser.driver)
    context.current_page.check_alarms_history(context)
