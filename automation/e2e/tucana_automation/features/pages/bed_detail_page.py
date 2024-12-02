import logging
import time

from selenium.common.exceptions import NoSuchElementException, TimeoutException
from selenium.webdriver.common.by import By
from selenium.webdriver.support.color import Color

from features.pages.base_page import BasePage
from datetime import date

class BedDetailPage(BasePage):

    left_bed_info = (By.XPATH, "//*[@data-testid='bed-card']")
    left_bed_info_name = (By.XPATH, "./div/div")
    bed_id_info = (By.XPATH, "//p[contains(text(),'Bed ID')]")
    hr_metric_card = (By.XPATH, "//*[@data-testid='hr-metric-card']")
    spo_metric_card = (By.XPATH, "//*[@data-testid='spo-metric-field']")
    rr_metric_card = (By.XPATH, "//*[@data-testid='rr-metric-card']")
    body_temp_metric_card = (By.XPATH, "//*[@data-testid='body-temp-metric-card']")
    pulse_metric_card_ = (By.XPATH, "//*[@data-testid='pulse-metric-card']")
    pulse_metric_card = (By.XPATH, "//div[contains(@class,'metricCardMiddleValue')]")
    bp_metric_card = (By.XPATH, "//*[@data-testid='bp-metric-card']")
    chest_temp_metric_card = (By.XPATH, "//*[@data-testid='chest-temp-metric-card']")
    limp_temp_metric_card = (By.XPATH, "//div[contains(@data-testid,'limb-temp-metric-card')]")
    fall_metric_card = (By.XPATH, "//*[@data-testid='fall-metric-card']")
    position_metric_card = (By.XPATH, "//*[@data-testid='position-metric-card position-sensors-connected']")
    top_alarms_box = (By.XPATH, "//*[@data-testid='vitals-alerts-list']")
    top_alarms_text = (By.XPATH, "//*[@data-testid='vitals-alerts-list']/span")
    top_alarms_number = (By.XPATH, "//*[@data-testid='vitals-alerts-list']/div")
    top_alerts_box = (By.XPATH, "//*[@data-testid='device-alerts-list']")
    top_alerts_text = (By.XPATH, "//*[@data-testid='device-alerts-list']/span")
    top_alerts_number = (By.XPATH, "//*[@data-testid='device-alerts-list']/div")
    left_alarms = (By.XPATH, "//*[@data-testid='vitals-alerts']")
    left_alerts = (By.XPATH, "//*[@data-testid='device-alerts']")
    tabs = (By.XPATH, "//button[text()='{}']")
    patient_id = (By.XPATH, "//p[text()='ID']//parent::div//following-sibling::div/p")
    patient_first_name = (
        By.XPATH,
        "//p[text()='First name']//parent::div//following-sibling::div/p",
    )
    patient_last_name = (
        By.XPATH,
        "//p[text()='Last name']//parent::div//following-sibling::div/p",
    )
    patient_sex = (By.XPATH, "//p[text()='Sex']//parent::div//following-sibling::div/p")
    patient_dob = (By.XPATH, "//p[text()='DOB']//parent::div//following-sibling::div/p")
    alarm_name = (By.XPATH, "//h6[text()='{}']")
    alarm_and_unit = (By.XPATH, "//td/span[text()='{}']/parent::td/following-sibling::td/span[text()='{}']")
    alarm = (
        By.XPATH,
        "//h6[text()='{}']//parent::div//following-sibling::div/h6[text()='{}']",
    )
    alarm_low_limit = (By.XPATH, "//td/span[text()='{}']/parent::td/following-sibling::td/following-sibling::td/span")
    alarm_high_limit = (By.XPATH, "//td/span[text()='{}']/parent::td/following-sibling::td/following-sibling::td/following-sibling::td/span")

    metric_cards = {
        "HR_Low_VISUAL": hr_metric_card,
        "HR_High_VISUAL": hr_metric_card,
        "RR_Low_VISUAL": rr_metric_card,
        "RR_High_VISUAL": rr_metric_card,
        "SPO2_Low_VISUAL": spo_metric_card,
        "SPO2_High_VISUAL": spo_metric_card,
        "PR_Low_VISUAL": pulse_metric_card,
        "PR_High_VISUAL": pulse_metric_card,
        "NIBP_SYS_Low_VISUAL": bp_metric_card,
        "NIBP_SYS_High_VISUAL": bp_metric_card,
        "NIBP_DIA_Low_VISUAL": bp_metric_card,
        "NIBP_DIA_High_VISUAL": bp_metric_card,
        "BODY_Temp_Low_VISUAL": body_temp_metric_card,
        "BODY_Temp_High_VISUAL": body_temp_metric_card,
        "CHEST_Skin_Temp_Low_VISUAL": chest_temp_metric_card,
        "CHEST_Skin_Temp_High_VISUAL": chest_temp_metric_card,
        "LIMB_Skin_Temp_Low_VISUAL": limp_temp_metric_card,
        "LIMB_Skin_Temp_High_VISUAL": limp_temp_metric_card,
        "FALL_VISUAL": fall_metric_card,
        "POSITION_VISUAL": position_metric_card
    }
    chest_sensor_icon = (By.XPATH, "//*[@data-testid='ANNE Chest-sensor-icon']")
    nonin_sensor_icon = (By.XPATH, "//*[@data-testid='Nonin 3150-sensor-icon']")
    thermometer_sensor_icon = (By.XPATH, "//*[@data-testid='DMT Thermometer-sensor-icon']")
    viatom_sensor_icon = (By.XPATH, "//*[@data-testid='Viatom BP monitor-sensor-icon']")
    adam_sensor_icon = (By.XPATH, "//*[@data-testid='ADAM-sensor-icon']")
    anne_limb_icon = (By.XPATH, "//*[@data-testid='ANNE Limb-sensor-icon']")

    sensor_ids = {
        "ANNE Chest": "ANNE Chest-sensor-icon",
        "Nonin 3150": "Nonin 3150-sensor-icon",
        "DMT Thermometer": "DMT Thermometer-sensor-icon",
        "Viatom BP monitor": "Viatom BP monitor-sensor-icon",
        "ADAM": "ADAM-sensor-icon",
        "ANNE Limb": "ANNE Limb-sensor-icon"
    }
    sensor_icons = {
        "ANNE Chest": chest_sensor_icon,
        "Nonin 3150": nonin_sensor_icon,
        "DMT Thermometer": thermometer_sensor_icon,
        "Viatom BP monitor": viatom_sensor_icon,
        "ADAM": adam_sensor_icon,
        "ANNE Limb": anne_limb_icon
    }

    anne_sensor_signal = (
        By.XPATH,
        "//*[@data-testid='{}']//parent::div//following-sibling::div//following-sibling::div//div//div/*",
    )
    anne_sensor_battery = (
        By.XPATH,
        "//*[@data-testid='{}']//parent::div//following-sibling::div//following-sibling::div//div//div//following-sibling::div/*",
    )

    sensor_name = (By.XPATH, "//h6[contains(text(),'{}')]")
    sensor_id = (By.XPATH, "//h6[contains(text(),'{}')]//following-sibling::h6")
    information_div = (By.XPATH, "//div[text()='{}']")
    information_h4 = (By.XPATH, "//h4[text()='{}']")
    spo_metric_field = (By.XPATH, "//*[@data-testid='spo-metric-field']")
    fall_metric_card = (By.XPATH, "//*[@data-testid='fall-metric-card']")
    position_metric_card = (
        By.XPATH,
        "//*[@data-testid='position-metric-card position-sensors-connected']",
    )
    chest_temp_metric_card = (By.XPATH, "//*[@data-testid='chest-temp-metric-card']")
    body_temp_metric_card = (By.XPATH, "//*[@data-testid='body-temp-metric-card']")
    limb_temp_metric_card = (
        By.XPATH,
        "//*[@data-testid='limb-temp-metric-card limb-temp-sensors-connected']",
    )
    pleth_metric_card = (
        By.XPATH,
        "//*[@data-testid='graph-card-without-vitals-alert']",
    )
    pr_metric_field = (
        By.XPATH,
        "//*[@data-testid='spo-metric-field']//following-sibling::div/h4",
    )
    pi_metric_field = (
        By.XPATH,
        "//*[@data-testid='spo-metric-field']//following-sibling::div//following-sibling::div/h4",
    )

    information_cards = {
        "HR (bpm)": hr_metric_card,
        "SPO2 (%)": spo_metric_field,
        "PR (bpm)": pr_metric_field,
        "PI (%)": pi_metric_field,
        "RR (brpm)": rr_metric_card,
        "FALL": fall_metric_card,
        "Position (HHMM)": position_metric_card,
        "BODY TEMP (°F)": body_temp_metric_card,
        "SKIN TEMP (°F)": chest_temp_metric_card,
        "NIBP (mmHg)": bp_metric_card,
        "PULSE (bpm)": pulse_metric_card_,
        "ECG": information_div,
        "PLETH": information_div,
        "RR": information_div,
    }
    left_panel_message = (By.XPATH, "//*[@data-testid='bed-card']/div/span[text()='{}']")
    left_panel_message_admit = (By.XPATH, "//*[@data-testid='bed-card']/div/h3[text()='{}']")
    pm_id = (By.XPATH, "//h6[contains(text(),'Patient Monitor ID')]//following-sibling::h6")
    specific_sensor_name = (By.XPATH, "//*[@data-testid='{}']/parent::div/following-sibling::div/h6")
    specific_sensor_id = (By.XPATH, "//*[@data-testid='{}']/parent::div/following-sibling::div/h6/following-sibling::h6")
    alert_texts = {"SENSOR_OUT_OF_RANGE": "OUT OF RANGE, MOVE SENSOR CLOSER",
                   "LEAD_OFF": "ECG LEAD-OFF",
                   "POOR_SKIN_CONTACT": "PPG POOR SKIN CONTACT",
                   "FINGER_NOT_DETECTED": "PPG POOR SKIN CONTACT",
                   "SENSOR_FAILURE": "SENSOR FAILURE, REPLACE SENSOR",
                   "SENSOR_ERROR": "SENSOR ERROR, RECONNECT SENSOR PROBE",
                   "SYSTEM_ERROR": "SYSTEM ERROR, RESTART SENSOR",
                   "MODULE_FAILURE": "SENSOR FAILURE, REPLACE SENSOR"
                   }
    alert_graph_card = (By.XPATH, "//*[@data-testid='alert-graph-card']")
    sensor_alert_icon = (By.XPATH, "//*[@data-testid='sensor-alert-icon']")
    alerts_with_warning_icon = ["SENSOR_FAILURE", "SENSOR_ERROR", "SYSTEM_ERROR"]
    sensor_unknown_data = (By.XPATH, "//span[text()='-?-']")
    bed_containers = (By.XPATH, "//*[@data-testid='graph-card-container']")
    top_alert_text_by_bed = (By.XPATH, "./div/div/*[@data-testid='device-alerts-list']/span")
    top_alarm_text_by_bed = (By.XPATH, "./div/div/*[@data-testid='vitals-alerts-list']/span")
    top_alarms_box_by_bed = (By.XPATH, "./div/div/*[@data-testid='vitals-alerts-list']")
    top_alerts_box_by_bed = (By.XPATH, "./div/div/*[@data-testid='device-alerts-list']")
    top_alarms_number_by_bed = (By.XPATH, "./div/div/*[@data-testid='vitals-alerts-list']/div")
    top_alerts_number_by_bed = (By.XPATH, "./div/div/*[@data-testid='device-alerts-list']/div")
    alarm_list = (By.XPATH, "//div[@role='presentation']//ul//li")

    def __init__(self, driver):
        super().__init__(driver)
        self.page_loading_time = time.time() - self.start_time

    def is_left_bed_info_completed(self, bed_name):
        try:
            left_info_index = None
            for index, bed in enumerate(
                self.web_utils.find_elements(*self.left_bed_info)
            ):
                if bed.find_element(*self.left_bed_info_name).text == bed_name:
                    left_info_index = index
                    break
                if index == len(self.web_utils.find_elements(*self.left_bed_info)) - 1:
                    return False
            if (
                len(
                    self.web_utils.find_elements(*self.left_bed_info)[
                        left_info_index
                    ].text.split("\n")
                )
                < 7
            ):
                return False
            else:
                return True
        except Exception:
            raise Exception("Can not get the left panel bed information")

    def check_card_alarm_color(self, alarm, level):
        try:
            card = self.web_utils.find_element(*self.metric_cards[alarm])
            card_rgb = card.value_of_css_property("background-color")
            card_background = Color.from_string(card_rgb).hex
            if card_background != self.alarm_level_colors[level]:
                for i in range(3):
                    logging.info("Waiting Alarm ...")
                    time.sleep(1)
                    card_rgb = card.value_of_css_property("background-color")
                    card_background = Color.from_string(card_rgb).hex
                    if card_background == self.alarm_level_colors[level]:
                        break
            card_rgb = card.value_of_css_property("background-color")
            card_background = Color.from_string(card_rgb).hex
            if level == 'OFF':
                if card_background == '#000000':
                    return True
                elif card_background == '#0d151c':
                    return True
                else:
                    return False
            else:
                return True if self.alarm_level_colors[level] == card_background else False
        except Exception as e:
            raise Exception(
                "Can not get the background attribute color of {}".format(alarm)
            )

    def check_top_alarm_all(self, alarm, level, alarm_type, number, index=0, multiview=False):
        time.sleep(1)
        self.check_top_alarm_label(alarm, alarm_type, index, multiview)
        self.check_top_alarm_color(level, alarm_type, index, multiview)
        self.check_top_alarm_index(number, alarm_type, index, multiview)
        return True

    def check_sensor_color(self, sensor_type, level):
        try:
            time.sleep(2)
            sensor_color_ok = False
            try:
                sensor = self.web_utils.find_element(*self.sensor_icons[sensor_type]).find_element(By.XPATH, "./child::*/child::*")
                sensor_rgb = sensor.get_attribute("fill").lower()
                top_alert_color = Color.from_string(sensor_rgb).hex
                if self.alarm_level_colors[level] == top_alert_color:
                    sensor_color_ok = True
            except NoSuchElementException:
                try:
                    sensor = self.web_utils.find_element(*self.sensor_icons[sensor_type]).find_element(By.XPATH, "./child::*")
                    sensor_rgb = sensor.get_attribute("fill").lower()
                    top_alert_color = Color.from_string(sensor_rgb).hex
                    if self.alarm_level_colors[level] == top_alert_color:
                        sensor_color_ok = True
                except NoSuchElementException:
                    raise Exception("Can not get the sensor's icon")
            if not sensor_color_ok:
                raise Exception(
                    f"Expected Top Indicator Color {self.alarm_level_colors[level]}, current {top_alert_color}"
                )
            return sensor_color_ok
        except NoSuchElementException:
            raise Exception("Can not get the sensor's icon")
        except Exception as e:
            raise Exception(f"Something went wrong with the sensor's icon color {e}")

    def check_alert_message(self, sensor_type, alarm):
        try:
            if alarm in self.alert_texts:
                text = self.alert_texts[alarm]
                alerts = self.web_utils.find_elements(*self.alert_graph_card)
                alerts_message_qty = 0
                for alert in alerts:
                    if alert.text == text:
                        alerts_message_qty += 1
                if sensor_type == 'ANNE Limb' or sensor_type == 'Nonin 3150':
                    if alerts_message_qty < 1:
                        raise Exception(f'{text} message should be present twice an it is not')
                elif sensor_type == 'Viatom BP monitor':
                    try:
                        if len(self.web_utils.find_elements(*self.sensor_unknown_data)) < 3:
                            raise Exception('-?- should be present x 3 and it is not')
                    except Exception:
                        raise Exception('Can not find the -?- when alert is present')
                else:
                    if alerts_message_qty < 2:
                        raise Exception(f'{text} message should be present twice an it is not')
        except Exception as e:
            raise Exception(f'Can not get the alert message information - {e}')

    def check_warning_icon_presence(self, alarm):
        try:
            if alarm in self.alerts_with_warning_icon:
                logging.info(f'{alarm} should have warning icon, checking icon presence')
                self.web_utils.find_element(*self.sensor_alert_icon)
        except Exception:
            raise Exception('Can not find the alert icon')

    def check_warning_icon_color(self, alarm, level):
        try:
            alert_color_ok = False
            if alarm in self.alerts_with_warning_icon:
                logging.info(f'{alarm} should have warning icon, checking icon color')
                alert_icon = self.web_utils.find_element(*self.sensor_alert_icon).find_element(By.XPATH, "./child::*")
                alert_rgb = alert_icon.get_attribute("fill").lower()
                top_alert_color = Color.from_string(alert_rgb).hex
                if self.alarm_level_colors[level] == top_alert_color:
                    alert_color_ok = True
                if not alert_color_ok:
                    raise Exception(
                        f"Expected Top Indicator Color {self.alarm_level_colors[level]}, current {top_alert_color}"
                    )
                return alert_color_ok
        except Exception:
            raise Exception('Can not find the alert icon')

    def check_top_alarm_label(self, alarm, alarm_type, bed_index=0, multiview=False):
        try:
            if 'AUDIO' in alarm:
                alarm_name = alarm.replace('AUDIO', '').replace('_', ' ')[:-1]
            else:
                if alarm == 'LEAD_OFF':
                    alarm_name = 'LEAD-OFF'
                elif alarm == 'MODULE_FAILURE':
                    alarm_name = 'Sensor failure'
                else:
                    alarm_name = alarm.replace('_', ' ')

            top_label_ok = False

            if alarm_type == 'Technical':
                if multiview:
                    top_alert_text = self.web_utils.find_elements(*self.bed_containers)[bed_index].find_element(
                        *self.top_alert_text_by_bed).text
                else:
                    top_alert_text = self.web_utils.find_element(*self.top_alerts_text).text
            else:
                if multiview:
                    top_alert_text = self.web_utils.find_elements(*self.bed_containers)[bed_index].find_element(*self.top_alarm_text_by_bed).text
                else:
                    top_alert_text = self.web_utils.find_element(*self.top_alarms_text).text
            if alarm_name == "POSITION":
                if "position" in top_alert_text.lower():
                    top_label_ok = True
            elif alarm_name == "FALL":
                if "fall" in top_alert_text.lower():
                    top_label_ok = True
            else:
                if top_alert_text.lower() == alarm_name.lower():
                    top_label_ok = True
            if not top_label_ok:
                raise Exception(
                    f"Expected Top Indicator label {alarm_name.upper()}, current {top_alert_text.upper()}"
                )

            return top_label_ok
        except Exception as e:
            raise Exception(f"Error in Top Indicator - {e}")

    def check_top_alarm_color(self, level, alarm_type, bed_index=0, multiview=False):
        try:
            top_color_ok = False
            if alarm_type == 'Technical':
                if multiview:
                    card = self.web_utils.find_elements(*self.bed_containers)[bed_index].find_element(*self.top_alerts_box_by_bed)
                else:
                    card = self.web_utils.find_element(*self.top_alerts_box)
            else:
                if multiview:
                    card = self.web_utils.find_elements(*self.bed_containers)[bed_index].find_element(*self.top_alarms_box_by_bed)
                else:
                    card = self.web_utils.find_element(*self.top_alarms_box)

            card_rgb = card.value_of_css_property("background-color")
            top_alert_color = Color.from_string(card_rgb).hex
            if self.alarm_level_colors[level] == top_alert_color:
                top_color_ok = True
            if not top_color_ok:
                raise Exception(
                    f"Expected Top Indicator Color {self.alarm_level_colors[level]}, current {top_alert_color}"
                )
            return top_color_ok
        except Exception as e:
            raise Exception(f"Error in Top level indicator - {e}")

    def check_top_alarm_index(self, number, alarm_type, bed_index=0, multiview=False):
        try:
            top_index_ok = False
            if alarm_type == 'Technical':
                if multiview:
                    top_alert_number = int(self.web_utils.find_elements(*self.bed_containers)[bed_index].find_element(*self.top_alerts_number_by_bed).text)
                else:
                    top_alert_number = int(self.web_utils.find_element(*self.top_alerts_number).text)
            else:
                if multiview:
                    top_alert_number = int(self.web_utils.find_elements(*self.bed_containers)[bed_index].find_element(*self.top_alarms_number_by_bed).text)
                else:
                    top_alert_number = int(self.web_utils.find_element(*self.top_alarms_number).text)
            if top_alert_number == number:
                top_index_ok = True
            if not top_index_ok:
                raise Exception(
                    f"Expected Top Indicator Index {number}, current {top_alert_number}"
                )
            return top_index_ok
        except Exception as e:
            raise Exception(f"Error in Top level indicator - {e}")

    def check_left_alarm(self, alarm_type, level, number):
        try:
            if alarm_type == 'Physiological':
                left_alarm_box = self.web_utils.find_element(*self.left_alarms)
            else:
                left_alarm_box = self.web_utils.find_element(*self.left_alerts)

            left_alert_text = left_alarm_box.text
            left_alert_color = Color.from_string(left_alarm_box.value_of_css_property("background-color")).hex

            if self.alarm_level_colors[level] == left_alert_color and int(left_alert_text) == number:
                return True
            else:
                return False
        except Exception:
            raise Exception("Can not get the Left alarm indicator")

    def no_left_alarms(self):
        time.sleep(1)
        try:
            self.web_utils.find_element(*self.left_alarms, retries=2, log_errors=False)
            return False
        except TimeoutException:
            return True

    def no_top_alarms(self, alarm_type):
        time.sleep(1)
        try:
            if alarm_type == 'Technical':
                self.web_utils.find_element(*self.top_alerts_box, retries=2, log_errors=False)
            else:
                self.web_utils.find_element(*self.top_alarms_box, retries=2, log_errors=False)
            return False
        except TimeoutException:
            return True

    def select_tab(self, tab_name):
        try:
            self.web_utils.find_element(
                self.tabs[0], self.tabs[1].format(tab_name.upper())
            ).click()
        except Exception:
            raise Exception(f"Can not select the {tab_name}")

    def get_patient_id(self):
        try:
            return self.web_utils.find_element(*self.patient_id).text
        except Exception:
            raise Exception(f"Can not find the patient ID information")

    def get_patient_first_name(self):
        try:
            return self.web_utils.find_element(*self.patient_first_name).text
        except Exception:
            raise Exception(f"Can not find the patient first name information")

    def get_patient_last_name(self):
        try:
            return self.web_utils.find_element(*self.patient_last_name).text
        except Exception:
            raise Exception(f"Can not find the patient last name information")

    def get_patient_sex(self):
        try:
            return self.web_utils.find_element(*self.patient_sex).text
        except Exception:
            raise Exception(f"Can not find the patient sex information")

    def get_patient_dob(self):
        try:
            return self.web_utils.find_element(*self.patient_dob).text
        except Exception:
            raise Exception(f"Can not find the patient dob information")

    def is_alarm_name_present(self, alarm_name):
        try:
            return (
                True
                if self.web_utils.find_element(
                    self.alarm_name[0], self.alarm_name[1].format(alarm_name)
                )
                else False
            )
        except Exception:
            raise Exception(
                f"Can not find the alarm name information inside vital management tab"
            )

    def is_alarm_present(self, alarm_name, unit):
        try:
            return (
                True
                if self.web_utils.find_element(
                    self.alarm_and_unit[0], self.alarm_and_unit[1].format(alarm_name, unit)
                )
                else False
            )
        except Exception:
            raise Exception(
                f"Can not find the alarm information inside vital management tab"
            )

    def get_alarm_low_limit(self, alarm_name):
        try:
            return self.web_utils.find_element(self.alarm_low_limit[0], self.alarm_low_limit[1].format(alarm_name)).text
        except Exception:
            raise Exception(
                f"Can not find the alarm low limit information inside vital management tab"
            )

    def get_alarm_high_limit(self, alarm_name):
        try:
            return self.web_utils.find_element(self.alarm_high_limit[0], self.alarm_high_limit[1].format(alarm_name)).text
        except Exception:
            raise Exception(
                f"Can not find the alarm high limit information inside vital management tab"
            )

    def verify_sensor_information(self, sensor_name, sensor_id):
        if sensor_name == "ANNE Chest":
            logging.info("ANNE CHEST SENSOR")
            self.anne_chest_data(sensor_name, sensor_id)
        elif sensor_name == "Nonin 3150":
            logging.info("NONIN SENSOR")
            self.common_sensor_info(sensor_name, sensor_id)
        elif sensor_name == "DMT Thermometer":
            logging.info("DMT SENSOR")
            self.common_sensor_info(sensor_name, sensor_id)
        elif sensor_name == "Viatom BP monitor":
            self.common_sensor_info(sensor_name, sensor_id)

    def anne_chest_data(self, sensor_name, sensor_id):
        try:
            self.web_utils.find_element(
                self.sensor_name[0], self.sensor_name[1].format(sensor_name)
            )
            if (
                not self.web_utils.find_element(
                    self.sensor_id[0], self.sensor_id[1].format(sensor_name)
                ).text
                == sensor_id
            ):
                raise Exception("Sensor ID doesn't match")
            try:
                self.web_utils.find_element(*self.chest_sensor_icon)
            except NoSuchElementException:
                raise Exception(f"Can not find {sensor_name} icon")
        except Exception as e:
            raise Exception(
                f"Something were wrong with the {sensor_name} information : {e}"
            )

    def common_sensor_info(self, sensor_name, sensor_id):
        sensor_icon = self.sensor_icons[sensor_name]
        try:
            self.web_utils.find_element(
                self.sensor_name[0], self.sensor_name[1].format(sensor_name)
            )
            if (
                not self.web_utils.find_element(
                    self.sensor_id[0], self.sensor_id[1].format(sensor_name)
                ).text
                == sensor_id
            ):
                raise Exception("Sensor ID doesn't match")
            try:
                self.web_utils.find_element(*sensor_icon)
            except NoSuchElementException:
                raise Exception(f"Can not find {sensor_name} icon")
        except Exception as e:
            raise Exception(
                f"Something were wrong with the {sensor_name} information : {e}"
            )

    def verify_vitals_information(self, information):
        try:
            if "ECG" in information or "PLETH" in information or "RR" in information:
                locator = self.information_cards[information]
                self.web_utils.find_element(locator[0], locator[1].format(information))
            else:
                vital = self.web_utils.find_element(
                    *self.information_cards[information]
                )
                vital_split = vital.text.split("\n")
                if len(vital_split) > 1:
                    if "Position" in information:
                        available_positions = [
                            "Upright",
                            "Supine",
                            "Left-L",
                            "Right-L",
                            "Prone",
                        ]
                        assert vital_split[0] in available_positions, (
                            "Position " + vital_split[0] + " not found"
                        )
                        assert (
                            vital_split[2] == "Lasted"
                        ), "Expected position time information LASTED, not found"
                        assert (
                            vital_split[4] == "h"
                        ), "Expected position time information HH, not found"
                        assert (
                            vital_split[6] == "m"
                        ), "Expected position time information MM, not found"
                    else:
                        assert vital_split[0] == information, (
                            "Expected " + information + " current " + vital_split[0]
                        )
                        logging.info(information + " found!")
                else:
                    assert vital.text == information, (
                        "Expected " + information + " current " + vital_split[0]
                    )
                    logging.info(information + " found!")
        except Exception:
            raise Exception(f"Something went wrong finding or matching {information}")

    def is_message_inside_left_card(self, message):
        try:
            time.sleep(5)
            if message == 'SELECT TO ADMIT PATIENT':
                return True if self.web_utils.find_element(self.left_panel_message_admit[0], self.left_panel_message_admit[1].format(message)) else False
            else:
                return True if self.web_utils.find_element(self.left_panel_message[0], self.left_panel_message[1].format(message)) else False
        except Exception:
            raise Exception(f'Can not find the {message} message inside the left panel')

    def is_data_inside_left_card(self, data1, data2):
        try:
            time.sleep(5)
            left_panel_text = self.web_utils.find_element(*self.left_bed_info).text
            if data1 in left_panel_text and data2 in left_panel_text:
                return True
            else:
                return False
        except Exception:
            raise Exception(f'Can not find {data1} or {data2} inside the left panel')

    def is_pm_id_present(self, ID):
        try:
            return True if self.web_utils.find_element(*self.pm_id).text.strip() == ID else False
        except Exception:
            raise Exception(f'Can not find the PM ID {ID} inside the bed detail page')

    def is_sensor_icon_present(self, sensor_type):
        try:
            return True if self.web_utils.find_element(*self.sensor_icons[sensor_type]).is_displayed() else False
        except Exception:
            raise Exception(f'Can not get the {sensor_type} sensor icon')

    def is_sensor_name_present(self, sensor_type):
        try:
            if self.web_utils.find_element(self.specific_sensor_name[0], self.specific_sensor_name[1].format(self.sensor_ids[sensor_type])).text == sensor_type:
                return True
            else:
                return False
        except Exception:
            raise Exception(f'Can not get the {sensor_type} sensor name')

    def is_sensor_id_present(self, sensor_type):
        try:
            return self.web_utils.find_element(self.specific_sensor_id[0], self.specific_sensor_id[1].format(self.sensor_ids[sensor_type])).text
        except Exception:
            raise Exception(f'Can not get the {sensor_type} sensor icon')

    def check_alarms_order(self, alarm_type):
        try:
            if alarm_type == 'alarms':
                self.web_utils.find_element(*self.top_alarms_box).click()
            else:
                self.web_utils.find_element(*self.top_alerts_box).click()
        except Exception as e:
            raise Exception('Can not find the alarm box')

        try:
            time.sleep(2)
            alarm_list = self.web_utils.find_elements(*self.alarm_list)
            alarms = []
            for alarm in alarm_list:
                if "chest sensor\n" in alarm.text.lower():
                    alarms.append(alarm.text.lower().replace('chest sensor\n', ''))
                elif "chest sensor/n" in alarm.text.lower():
                    alarms.append(alarm.text.lower().replace('chest sensor/n', ''))
                else:
                    alarms.append(alarm.text.lower())
            return alarms
        except Exception:
            raise Exception('Can not find the list')

    def check_alarms_history(self, context):
        messages_physiological = {'HR_Low_VISUAL': 'HR value is below the lower alarm limit.',
                                  'HR_High_VISUAL': 'HR value is above the upper alarm limit.',
                                  'RR_Low_VISUAL': 'RR value is below the lower alarm limit.',
                                  'RR_High_VISUAL': 'RR value is above the upper alarm limit.',
                                  'CHEST_Skin_Temp_Low_VISUAL': 'Chest Skin Temp value is below the lower alarm limit.',
                                  'CHEST_Skin_Temp_High_VISUAL': 'Chest Skin Temp value is above the upper alarm limit.',
                                  'FALL_VISUAL': 'A fall has been detected.',
                                  'POSITION_VISUAL': 'Patient has been in the current position for more than 2 hours.',
                                  }
        messages_technicals = {'SENSOR_OUT_OF_RANGE': 'Sensor is not detected nearby. Datastream will not be available. The application will automatically attempt to reconnect to the sensor after the signal is detected.',
                               'LEAD_OFF': 'Chest sensor is not detecting good contact with the skin.',
                               'MODULE_FAILURE': 'Chest Sensor has reported a sensor failure. The sensor should be replaced immediately.'}

        alarm_levels = {'HI': 'High', 'ME': 'Medium', 'LO': 'Low'}
        alarm_type = {'physiological': 'vitals', 'technical': 'device'}
        time.sleep(2)
        try:
            rows = self.web_utils.find_elements(By.XPATH, "//table/tbody/tr")
            rows.reverse()
            for i, alarm in enumerate(context.activated_history):
                columns = rows[i].find_elements(By.TAG_NAME, 'td')
                logging.info(f'Verifying Row {i} - Row Data : {rows[i].text}')
                for index, column in enumerate(columns):
                    if index == 0 and column.text != alarm_type[alarm[6]]:
                        logging.info(column.text)
                        raise Exception("Alarm type doesn't match")
                    elif index == 1 and column.text != date.today().strftime("%Y-%m-%d"):
                        logging.info(column.text)
                        raise Exception("Alarm date doesn't match")
                    elif index == 2 and column.text is None:
                        logging.info(column.text)
                        raise Exception('Alarm time column is empty and it should not')
                    elif index == 3 and column.text != alarm_levels[alarm[3]]:
                        logging.info(column.text)
                        raise Exception("Alarm level doesn't match")
                    elif index == 4:
                        if alarm[6] == 'physiological':
                            if column.text != messages_physiological[alarm[4]]:
                                logging.info(column.text)
                                logging.info(messages_physiological[alarm[4]])
                                raise Exception("Alarm message doesn't match")
                        elif alarm[6] == 'technical':
                            if column.text != messages_technicals[alarm[4]]:
                                logging.info(column.text)
                                logging.info(messages_technicals[alarm[4]])
                                raise Exception("Alarm message doesn't match")
                    elif index == 5 and column.text != '00:00:0' + alarm[5]:
                        logging.info(column.text)
                        raise Exception("Alarm time doesn't match")
                    else:
                        logging.info(f'Row {i} Verified OK !')
                        break
        except Exception as e:
            raise Exception(f'{e}')
