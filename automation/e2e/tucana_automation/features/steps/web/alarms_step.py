import logging
import random
import time

from behave import *

from features.pages.bed_detail_page import BedDetailPage
from features.pages.dashboard_page import DashboardPage
from features.steps.api.emulator import (
    physiological_alerts_and_alarms_codes, sensors, physiological_audio_alert_alarms_codes,
    technical_alerts_and_alarms_codes,
)
from features.steps.api.common_api_steps import verify_request_status
from features.steps.web.common_steps import fills_password_information, go_to_settings
from utils.api_utils import set_alarm_to_patient


@step('Tom triggers all "{}" alarms and checks "{}" colors, of "{}", id "{}" with different priorities, duration {} seconds')
@step('Tom triggers all "{}" alarms and checks "{}" colors, of "{}", id "{}" with different priorities')
@step('Tom triggers all "{}" alarms and checks "{}" colors, of "{}", id "{}", alert messages and warning icon with different priorities')
def checking_alarms_status(context, alarms_type, position, sensor_type, sensor_id, duration=0):
    context.alarm_type = alarms_type
    context.activated_alarms = []
    context.activated_history = []
    for row in context.table:
        if alarms_type == 'Physiological':
            alarms = sensors[sensor_type]['Physiological']
            logging.info(f"Testing these Alarms {alarms}")
            for alarm in alarms:
                if position == 'Top/Left':
                    alarm = alarm + '_AUDIO'
                    alarm_code = physiological_audio_alert_alarms_codes[alarm]
                else:
                    alarm = alarm + '_VISUAL'
                    alarm_code = physiological_alerts_and_alarms_codes[alarm]
                logging.info("Triggering the {} Alarm".format(alarm))
                context.response = set_alarm_to_patient(context, context.patient_primary_id, alarm_code, row['Priority'], True, sensor_type, sensor_id)
                verify_request_status(context, 204, "No Content")

                context.activated_alarms.append([sensor_type, sensor_id, context.patient_primary_id, row['Priority'], alarm_code])
                context.activated_history.append([sensor_type, sensor_id, context.patient_primary_id, row['Priority'], alarm, duration, 'physiological'])
                if position == 'Top/Left':
                    top_alarm_color_label_and_number(context, alarm, row['Priority'], alarms_type, 1)
                else:
                    card_alarm_color(context, alarm, row['Priority'])
                # Set alarm duration
                time.sleep(int(duration))
                # Disabling Alarm
                set_alarm_to_patient(context, context.patient_primary_id, alarm_code, row['Priority'], False, sensor_type, sensor_id)
                verify_request_status(context, 204, "No Content")
                context.activated_alarms.pop()
                if position == 'Top/Left':
                    check_alarm_off_top_left(context, alarm, alarms_type)
                else:
                    check_card_alarm_off(context, alarm)
        else:
            alerts = sensors[sensor_type]['Technical']
            for alert in alerts:
                alarm_code = technical_alerts_and_alarms_codes[alert]
                logging.info("Triggering the {} Technical Alarm".format(alert))
                context.response = set_alarm_to_patient(context, context.patient_primary_id, alarm_code, row['Priority'], True, sensor_type, sensor_id)
                verify_request_status(context, 204, "No Content")
                context.activated_alarms.append([sensor_type, sensor_id, context.patient_primary_id, row['Priority'], alarm_code])
                context.activated_history.append([sensor_type, sensor_id, context.patient_primary_id, row['Priority'], alert, duration, 'technical'])
                top_alarm_color_label_and_number(context, alert, row['Priority'],  alarms_type, 1)
                context.current_page.check_sensor_color(sensor_type, row['Priority'])
                logging.info("Verify Alert Message presence if necessary")
                context.current_page.check_alert_message(sensor_type, alert)
                logging.info("Verify Warning Icon presence if necessary")
                context.current_page.check_warning_icon_presence(alert)
                logging.info("Verify Warning Icon Color if necessary")
                context.current_page.check_warning_icon_color(alert, row['Priority'])
                # Disabling Alarm
                set_alarm_to_patient(context, context.patient_primary_id, alarm_code, row['Priority'], False, sensor_type, sensor_id)
                verify_request_status(context, 204, "No Content")
                context.activated_alarms.pop()
                check_alarm_off_top_left(context, alert, alarms_type)


def card_alarm_color(context, alarm_name, priority):
    logging.info("Checking Card {} alarm Color".format(alarm_name))
    context.current_page = BedDetailPage(context.browser.driver)
    assert context.current_page.check_card_alarm_color(
        alarm_name, priority
    ), "The {} color in {} priority, is not correct".format(alarm_name, priority)


def top_alarm_color_label_and_number(context, alarm_name, priority, alarm_type, number, index=0, multiview=False):
    logging.info("Checking {} Top alarm Color and label".format(alarm_name))
    context.current_page = BedDetailPage(context.browser.driver)
    assert context.current_page.check_top_alarm_all(alarm_name, priority, alarm_type, number, index, multiview), "Something went wrong with the top alarm indicator"


def left_alarm_color_and_number(context, alarm_type, priority, number):
    logging.info("Checking Left alarm Color and number")
    assert context.current_page.check_left_alarm(alarm_type, priority, number), "Something went wrong with the left alarm indicator"


def deactivate_alarm(context, alarm_name, priority, patient_id):
    logging.info("Deactivating the {} Alarm".format(alarm_name))
    context.response = set_alarm_to_patient(
        context,
        patient_id,
        physiological_alerts_and_alarms_codes[alarm_name],
        priority,
        False,
    )
    verify_request_status(context, 204, "No Content")
    time.sleep(2)


def check_card_alarm_off(context, alarm_name):
    logging.info("Checking Card alarm {} indicator is deactivated".format(alarm_name))
    assert context.current_page.check_card_alarm_color(
        alarm_name, "OFF"
    ), "The {} color deactivated is not correct".format(alarm_name)


def check_alarm_off_top_left(context, alarm_name, alarm_type):
    logging.info("Checking Card alarm {} indicator is deactivated".format(alarm_name))
    logging.info("Checking Left alarm indicator is deactivated")
    assert context.current_page.no_left_alarms(), "The left alarm is still present"
    logging.info("Checking Top alarm indicator is deactivated")
    assert context.current_page.no_top_alarms(alarm_type), "The top alarm is still present"


def check_alarm_off_top(context, alarm_type):
    logging.info("Checking Top alarm indicator is deactivated")
    assert context.current_page.no_top_alarms(alarm_type), "The top alarm is still present"


@step('Multiple "{}" "{}" alarms with "{}" priority, "{}", "{}" are triggered')
def trigger_multiple_alarms(context, alarm_type, alarm_code_list, priority, sensor_type, sensor_id):
    alarms = alarm_code_list.split(",")
    context.alarm_code_list = alarms
    context.alarm_priority = priority.split(",")
    context.alarm_type = alarm_type
    context.activated_alarms = []
    if alarm_type == 'Physiological':
        for index, alarm in enumerate(alarms):
            card_alarm = alarm.strip() + '_AUDIO'
            alarm_code = physiological_audio_alert_alarms_codes[card_alarm]
            logging.info("Triggering the {} Alarm".format(card_alarm))
            trigger_alarm(context, context.patient_primary_id, alarm_code, context.alarm_priority[index].strip(), True, sensor_type, sensor_id)
            time.sleep(2)
            alarm_top_left = alarm.strip() + '_VISUAL'
            alarm_code = physiological_alerts_and_alarms_codes[alarm_top_left]
            trigger_alarm(context, context.patient_primary_id, alarm_code, context.alarm_priority[index].strip(), True, sensor_type, sensor_id)
    else:
        for index, alert in enumerate(alarms):
            alert_alarm = alert.strip()
            alarm_code = technical_alerts_and_alarms_codes[alert_alarm]
            logging.info("Triggering the {} Technical Alarm".format(alert_alarm))
            trigger_alarm(context, context.patient_primary_id, alarm_code, context.alarm_priority[index].strip(), True, sensor_type, sensor_id)
            time.sleep(2)


@step('Trigger alarm with this parameters {} {} {} {} {} {}')
def trigger_alarm(context, patient_primary_id, alarm_code, priority, activate, sensor_type, sensor_id):
    context.response = set_alarm_to_patient(context, patient_primary_id, alarm_code, priority, activate, sensor_type, sensor_id)
    verify_request_status(context, 204, "No Content")
    context.activated_alarms.append([sensor_type, sensor_id, context.patient_primary_id, priority, alarm_code])


@step("Tom sees all the Cards activated with the correct color")
def check_all_cards_activated(context):
    time.sleep(1)
    for index, alarm in enumerate(context.alarm_code_list):
        alarm_name = alarm.strip() + '_VISUAL'
        card_alarm_color(context, alarm_name, context.alarm_priority[index].strip())


@step('Tom sees the top level indicator showing the last "{}" alarm name triggered and the total')
def check_top_level_last_alarm_and_number(context, alarm_type):
    time.sleep(3)
    number_of_alarms = len(context.alarm_code_list)
    last_alarm_name = context.alarm_code_list[number_of_alarms - 1]
    if alarm_type == 'Physiological':
        top_alarm_color_label_and_number(
            context,
            last_alarm_name.strip() + '_AUDIO',
            context.alarm_priority[0],
            context.alarm_type,
            number_of_alarms
        )
    else:
        top_alarm_color_label_and_number(
            context,
            last_alarm_name.strip(),
            context.alarm_priority[0],
            context.alarm_type,
            number_of_alarms
        )


@step('Tom sees the top level indicator showing the "{}" alarm name triggered with highest priority and the total')
def check_top_level_highest_alarm_and_number(context, alarm_type):
    time.sleep(3)
    number_of_alarms = len(context.alarm_code_list)
    highest_alarm_name = context.alarm_code_list[0]
    if alarm_type == 'Physiological':
        top_alarm_color_label_and_number(
            context,
            highest_alarm_name.strip() + '_AUDIO',
            context.alarm_priority[0],
            context.alarm_type,
            number_of_alarms
        )
    else:
        top_alarm_color_label_and_number(
            context,
            highest_alarm_name.strip(),
            context.alarm_priority[0],
            context.alarm_type,
            number_of_alarms
        )


@step("Tom deactivate all the triggered alarms")
def deactivate_all_alarms(context):
    clean_activated_alarms(context)


@step('Tom sees the left "{}" alarm indicator showing the total number of alarms triggered')
def left_alarm_total(context, alarm_type):
    number_of_alarms = len(context.alarm_code_list)
    if isinstance(context.alarm_priority, list):
        left_alarm_color_and_number(context, alarm_type, context.alarm_priority[0], number_of_alarms)
    else:
        left_alarm_color_and_number(context, alarm_type, context.alarm_priority, number_of_alarms)


@step("Tom should not see any alarm or top level indicators activated")
def no_indicator(context):
    for alarm in context.alarm_code_list:
        if context.alarm_type == 'Technical':
            alarm_name = alarm
            check_alarm_off_top_left(context, context.alarm_type, alarm_name)
        else:
            alarm_name = alarm.strip() + '_VISUAL'
            check_card_alarm_off(context, alarm_name)
            alarm_name = alarm.strip() + '_AUDIO'
            check_alarm_off_top_left(context, context.alarm_type, alarm_name)


@step("Tom should not see the top level indicators activated")
def no_indicator(context):
    check_alarm_off_top(context, context.alarm_type)


@step("Tom clicks on Manage audio alarm")
def manage_audio_alarm(context):
    context.current_page.click_on_manage_audio_alarm()


@step('Tom sees the alarm is "{}"')
def check_alarm_status(context, status):
    assert context.current_page.check_alarm_status(status), (
        "Not the expected " + status + " status"
    )


@step("Tom sees the actual alarm status")
def get_alarm_status(context):
    context.current_alarm_status = context.current_page.get_current_alarm_status()


@step('Tom turns the alarm "{}"')
def change_alarm_status(context, status):
    context.current_page.change_alarm_status(status)


@step("Tom changes the alarm status")
def changes_alarm_status(context):
    if context.current_alarm_status == "activated":
        context.current_page.change_alarm_status("OFF")
        context.current_alarm_status = "deactivated"
    elif context.current_alarm_status == "deactivated":
        context.current_page.change_alarm_status("ON")
        context.current_alarm_status = "activated"


@step("Tom saves the alarm status")
def save_alarm_status(context):
    context.current_page.save_alarm_status()


@step("Tom verifies the new alarm status")
def verify_new_alarm_status(context):
    if context.current_alarm_status == "activated":
        context.current_page.check_alarm_status("ON")
    elif context.current_alarm_status == "deactivated":
        context.current_page.check_alarm_status("OFF")


@step("Tom confirms the alarm is activated")
def confirms_alarm_activated(context):
    get_alarm_status(context)
    if context.current_alarm_status != "activated":
        go_to_settings(context)
        manage_audio_alarm(context)
        change_alarm_status(context, "ON")
        fills_password_information(context)
        alarm_status_mod_success(context)
        check_alarm_status(context, "activated")


@step("Tom sees the alarm status successful modification message")
def alarm_status_mod_success(context):
    context.current_page.alarm_status_modified()


@step("Tom sees the Pause Alarm button")
def pause_alarm_presence(context):
    assert context.current_page.is_pause_alarm_present()


@step("Tom pauses the Alarm sound")
def pause_alarm(context):
    context.current_page.pause_alarm()


@step("Tom sees the 2 minutes countdown")
def two_minutes_countdown(context):
    assert context.current_page.is_alarm_paused()


@step("Tom deactivate the countdown")
def deactivate_countdown(context):
    context.current_page.deactivate_countdown()


@step('Tom sees the "{}" icon, name and ID "{}" present')
def sees_sensor_info(context, sensor_type, id):
    context.current_page = BedDetailPage(context.browser.driver)
    time.sleep(3)
    assert context.current_page.is_sensor_icon_present(sensor_type), f'Sensor {sensor_type} icon was not present'
    sensor_id = context.current_page.is_sensor_id_present(sensor_type)
    assert sensor_id == id, f'Expected id {id}, current {sensor_id}'
    assert context.current_page.is_sensor_name_present(sensor_type), f'Sensor {sensor_type} name was not present'


def clean_activated_alarms(context):
    if "activated_alarms" in context:
        if len(context.activated_alarms) > 0:
            for alarm in context.activated_alarms.copy():
                sensor_type = alarm[0]
                sensor_id = alarm[1]
                patient_id = alarm[2]
                priority = alarm[3]
                alarm_code = alarm[4]
                context.response = set_alarm_to_patient(context, patient_id, alarm_code, priority, False, sensor_type, sensor_id)
                verify_request_status(context, 204, "No Content")
                context.activated_alarms.remove(alarm)


@step('{} Technical and Physiological HI priority alarm are trigger for each patient, color, number and text are verified')
def checking_alarms_status_multiple_beds(context, sensor_type, priority='HI'):
    alarms = sensors[sensor_type]['Physiological']
    alerts = sensors[sensor_type]['Technical']
    context.activated_alarms = []
    for index in range(len(context.beds)):
        time.sleep(4)
        random_physiological_alarm = random.randint(0, len(alarms)-1)
        logging.info(f"Testing this physiological Alarm {alarms[random_physiological_alarm]}")
        dashboard_page = DashboardPage(context.browser.driver)
        bed_id = dashboard_page.identify_bed(index)
        logging.info(f'Working in the {bed_id}')
        pm_id = context.pm_to_beds[context.bed_name_and_id[bed_id.strip('Bed ID ')]]
        pm_name = [i for i in context.pm_name_ids if context.pm_name_ids[i] == pm_id][0]
        context.patient_emulator_data = context.patient_ed_pm_name[pm_name]

        context.patient_primary_id = context.patient_emulator_data['patient']['primary_identifier']
        sensor_id = [i for i in context.pm_names_sensor_id if context.pm_names_sensor_id[i] == pm_name][0]

        alarm = alarms[random_physiological_alarm].strip() + '_AUDIO'
        logging.info("Triggering the {} Alarm".format(alarm))
        alarm_code = physiological_audio_alert_alarms_codes[alarm]

        context.response = set_alarm_to_patient(context, context.patient_primary_id, alarm_code, priority, True, sensor_type, sensor_id)
        verify_request_status(context, 204, "No Content")
        context.activated_alarms.append([sensor_type, sensor_id, context.patient_primary_id, priority, alarm_code])

        top_alarm_color_label_and_number(context, alarm, priority, "Physiological", 1, index, True)

        random_technical_alert = random.randint(0, len(alerts)-1)
        alert_alarm = alerts[random_technical_alert].strip()
        alert_code = technical_alerts_and_alarms_codes[alert_alarm]
        logging.info("Triggering the {} Technical Alarm".format(alerts[random_technical_alert]))
        context.response = set_alarm_to_patient(context, context.patient_primary_id, alert_code, priority, True, sensor_type, sensor_id)
        verify_request_status(context, 204, "No Content")

        context.activated_alarms.append([sensor_type, sensor_id, context.patient_primary_id, priority, alert_code])

        top_alarm_color_label_and_number(context, alert_alarm, priority, "Technical", 1, index, True)


@step("Tom deactivate all sensors alarms")
def deactivate_sensors_alarms_and_alerts(context):
    clean_activated_alarms(context)


@step("Tom clicks on the {} and sees them ordered by highest priority")
def check_descending_order(context, alarm_type):
    bed_detail = BedDetailPage(context.browser.driver)
    alarm_list = bed_detail.check_alarms_order(alarm_type)
    alarm_levels = {"HI": 1, "ME": 2, "LO": 3}
    alarm_and_level = []
    for index, alarm in enumerate(context.alarm_code_list):
        if alarm.strip() == 'FALL':
            alarm = 'fall detected'
        else:
            alarm = alarm.replace('_', " ").lower().strip()
        data = (alarm, alarm_levels[context.alarm_priority[index].strip()])
        alarm_and_level.append(data)

    alarm_sorted = sorted(sorted(alarm_and_level), key=lambda x: x[1])
    alarm_sorted_list = []
    for i in range(len(alarm_sorted)):
        alarm_sorted_list.append(alarm_sorted[i][0])

    assert alarm_list == alarm_sorted_list, f"Expected alarm list {alarm_sorted_list}, current {alarm_list}"


@step("Tom tries to close the alarm popup")
def close_alarm_popup(context):
    context.current_page.dismiss_modal()


@step('Tom should see the "{}" message')
def is_audio_off_message_present(context, message):
    context.current_page = DashboardPage(context.browser.driver)
    assert context.current_page.is_audio_off_signal_present()


@step('Tom should not see the "{}" message')
def is_audio_off_message_not_present(context, message):
    context.current_page = DashboardPage(context.browser.driver)
    assert not context.current_page.is_audio_off_signal_present()
