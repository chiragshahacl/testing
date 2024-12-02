import logging
import time

from selenium.common.exceptions import NoSuchElementException, TimeoutException
from selenium.webdriver.common.by import By
from selenium.webdriver.support.color import Color

from features.pages.base_page import BasePage


class DashboardPage(BasePage):
    anne_logo = (By.XPATH, "//img[@alt='anne-stream-logo']")

    bed_management_btn = (By.XPATH, "//p[text()='Bed Management']//ancestor::button")
    group_management_btn = (
        By.XPATH,
        "//p[text()='Group Management']//ancestor::button",
    )
    settings = (By.XPATH, "//p[text()='Settings']//ancestor::button")

    log_out_button = (By.XPATH, "//button[text()='Log out']")
    manage_audio_alarm_button = (By.XPATH, "//button[text()='Manage audio alarm']")
    log_out_password_field = (By.XPATH, "//input[@name='password']")
    confirm_btn = (By.XPATH, "//button[text()='Confirm']")
    log_out_error_msg = (
        By.XPATH,
        "//p[text()='Incorrect password. Please try again.']",
    )
    specific_group_in_dashboard = (
        By.XPATH,
        "//div[@id='horizontal-list-container']/ul/li",
    )

    individual_bed_name_div = (
        By.XPATH,
        "//div[@class='container']/div/div/div/div[text()='{}']",
    )
    individual_bed_name_p = (
        By.XPATH,
        "//div[@class='container']/div/div/p[text()='{}']",
    )
    bed_graph = (By.CSS_SELECTOR, "[id^='graph']")
    beds = (By.XPATH, "//div[@class='container']/div")
    specific_patient_bed = (By.XPATH, "//span[text()='{}']")
    patient_bed_id = (By.XPATH, "//span[text()='{}']//preceding-sibling::p")
    specific_top_alerts_dashboard = (
        By.XPATH,
        "//div[@class='container']/div/div/span[text()='{}']/following-sibling::div/button[@data-testid='vitals-alerts-list']",
    )
    specific_top_alerts_dashboard_text = (
        By.XPATH,
        "//div[@class='container']/div/div/span[text()='{}']/following-sibling::div/button[@data-testid='vitals-alerts-list']/span",
    )
    specific_top_alerts_dashboard_number = (
        By.XPATH,
        "//div[@class='container']/div/div/span[text()='{}']/following-sibling::div/button[@data-testid='vitals-alerts-list']/div",
    )
    options = {
        "Group Management": group_management_btn,
        "Bed Management": bed_management_btn,
    }
    change_password_btn = (By.XPATH, "//button[text()='Change password']")
    new_password_field = (By.XPATH, "//input[@name='newPassword']")
    re_enter_password_field = (By.XPATH, "//input[@name='reEnteredPassword']")
    password_error_message = (By.XPATH, "//p[text()='{}']")
    audio_off = (By.XPATH, "//p[text()='Central Audio Off']")
    audio_on = (By.XPATH, "//p[text()='Central Audio on']")
    settings_audio_off = (By.XPATH, "//p[text()='OFF']")
    settings_audio_on = (By.XPATH, "//p[text()='ON']")
    save_button = (By.XPATH, "//button[text()='Save']")
    alarm_modified = (By.XPATH, "//h1[text()='Alarm settings updated']")
    alarm_modified_ok = (By.XPATH, "//button[text()='Ok']")
    pause_alarm_btn = (By.XPATH, "//button[text()='Pause']")
    alarm_paused = (By.XPATH, "//p[contains(text(),'Paused')]")
    cancel_countdown = (By.XPATH, "//button[text()='Cancel']")
    confirm_btn_status = (By.XPATH, "//*[@data-testid='submit-button']")
    multi_patient_view = (By.XPATH, "//*[@data-testid='active-group-beds']")
    password_required = (By.XPATH, "//h1[text()='Password required']")
    current_password = (By.XPATH, "//h6[contains(text(),'current password')]")
    change_password_title = (By.XPATH, "//h1[text()='Change password']")
    change_password_requirements_tooltip = (By.XPATH, "//div[@role='tooltip']")
    confirm_btn_password_status = (By.XPATH, "//button[@type='submit']")
    password_required_at_change = (By.XPATH, "./p[text()='Password is required.']")
    dashboard_bed_message = (By.XPATH, "//span[text()='{}']")
    dashboard_bed_message_search = (By.XPATH, "//p[text()='{}']")
    patient_info = (By.XPATH, "//button[text()='PATIENT INFO']")
    alarm_history = (By.XPATH, "//*[@data-testid='ALARM HISTORY']")
    multi_patient_view_beds = (By.XPATH, "//*[@data-testid='active-group-beds']/div")
    dismiss_modal_btn = (By.XPATH, "//*[@data-testid='dismiss-modal']")
    audio_password_popup_info = (By.XPATH, "//h6[text()='All audible alarms at Central Station will be silenced until manually activated. Please enter the password to save alarm settings.']")
    audio_off_at_bedside = (By.XPATH, "//h6[text()='Audio Off at bedside']")

    def __init__(self, driver):
        super().__init__(driver)
        self.page_loading_time = time.time() - self.start_time

    def is_anne_logo_present(self):
        try:
            return (
                True
                if self.web_utils.find_element(
                    *self.anne_logo, retries=20, log_errors=False
                ).is_displayed()
                else False
            )
        except Exception:
            return False

    def go_to_settings(self):
        time.sleep(3)
        try:
            self.web_utils.find_element(*self.settings).click()
        except Exception:
            raise Exception("Something went wrong with the setting button")

    def log_out(self):
        try:
            self.web_utils.find_element(*self.log_out_button).click()
        except Exception:
            raise Exception("Something went wrong with the log out button")

    def logout_password(self, password):
        try:
            password_field = self.web_utils.find_element(*self.log_out_password_field)
            password_field.click()
            password_field.send_keys(password)
            time.sleep(2)
        except Exception:
            raise Exception("Something went wrong with the logout password form")

    def confirm_button_status(self):
        try:
            return (
                self.driver.find_element(By.TAG_NAME, "form")
                .find_element(*self.confirm_btn_status)
                .is_enabled()
            )
        except Exception:
            raise Exception("Can not find the confirm button")

    def confirm_password_button_status(self):
        try:
            return (
                self.driver.find_element(By.TAG_NAME, "form")
                .find_element(*self.confirm_btn_password_status)
                .is_enabled()
            )
        except Exception:
            raise Exception("Can not find the confirm button")

    def click_on_confirm_button(self):
        try:
            self.web_utils.find_element(*self.confirm_btn).click()
        except Exception:
            raise Exception("Can not find the confirm button")

    def multi_patient_view_presence(self):
        try:
            multi_patient_view = self.web_utils.find_element(*self.multi_patient_view)
            return True if multi_patient_view.is_displayed() else False
        except Exception:
            raise Exception("Can not find the multi patient view")

    def click_on_option(self, option):
        try:
            time.sleep(3)
            self.web_utils.find_element(*self.options[option]).click()
        except Exception:
            raise Exception("Can not click on option: {}".format(option))

    def log_out_incorrect_password(self):
        try:
            return (
                True
                if self.web_utils.find_element(*self.log_out_error_msg).is_displayed()
                else False
            )
        except Exception:
            raise Exception("The incorrect log out password message was not here")

    def is_new_group_in_dashboard(self, group_name):
        try:
            groups = self.web_utils.find_elements(
                *self.specific_group_in_dashboard, retries=5
            )
            for group in groups:
                if group.text == group_name:
                    return True
        except Exception:
            return False

    def click_group_in_dashboard(self, group_name):
        time.sleep(4)
        try:
            groups = self.web_utils.find_elements(
                *self.specific_group_in_dashboard, retries=5
            )
            for index, group in enumerate(groups):
                if group.text == group_name:
                    self.web_utils.find_elements(
                        *self.specific_group_in_dashboard, retries=5
                    )[index].click()
                    time.sleep(3)
                    break

        except Exception as e:
            raise Exception(
                "Something went wrong trying to click on {}, {}".format(
                    group_name, str(e)
                )
            )

    def is_bed_in_groups(self, expected_bed_name):
        try:
            return (
                True
                if self.web_utils.find_element(
                    self.individual_bed_name_div[0],
                    self.individual_bed_name_div[1].format(expected_bed_name),
                    retries=3,
                    log_errors=False,
                ).is_displayed()
                else False
            )
        except Exception:
            try:
                return (
                    True
                    if self.web_utils.find_element(
                        self.individual_bed_name_p[0],
                        self.individual_bed_name_p[1].format(expected_bed_name),
                        retries=3,
                        log_errors=False,
                    ).is_displayed()
                    else False
                )
            except Exception:
                return False

    def get_bed_names(self):
        beds = self.web_utils.find_elements(*self.beds)
        bed_names = []
        for bed in beds:
            bed_information = bed.text.split("\n")
            bed_names.append(bed_information[0])
        return bed_names

    def get_beds_qty(self):
        return len(self.web_utils.find_elements(*self.beds))

    def get_bed_info(self, index):
        try:
            return self.web_utils.find_elements(*self.beds)[index].text
        except Exception:
            raise Exception("Can not get the bed information")

    def get_dashboard_groups(self):
        time.sleep(3)
        groups = self.web_utils.find_elements(*self.specific_group_in_dashboard)
        group_names = []
        for group in groups:
            group_names.append(group.text)
        return group_names

    def select_patient_bed(self, patient):
        try:
            self.web_utils.find_element(
                self.specific_patient_bed[0],
                self.specific_patient_bed[1].format(patient),
            ).click()
        except Exception:
            raise Exception("Can not select the patient {} bed ".format(patient))

    def get_patient_bed_id(self, patient):
        try:
            return self.web_utils.find_element(
                self.patient_bed_id[0], self.patient_bed_id[1].format(patient)
            ).text
        except Exception:
            raise Exception("Can not get the patient {} bed ID ".format(patient))

    def is_top_alarm_enabled(self, alarm, level, patient_name, number):
        try:
            card = self.web_utils.find_element(
                self.specific_top_alerts_dashboard[0],
                self.specific_top_alerts_dashboard[1].format(patient_name),
            )
            card_rgb = card.value_of_css_property("background-color")
            top_alert_color = Color.from_string(card_rgb).hex
            top_alert_text = self.web_utils.find_element(
                self.specific_top_alerts_dashboard_text[0],
                self.specific_top_alerts_dashboard_text[1].format(patient_name),
            ).text
            top_alert_number = int(
                self.web_utils.find_element(
                    self.specific_top_alerts_dashboard_number[0],
                    self.specific_top_alerts_dashboard_number[1].format(patient_name),
                ).text
            )
            if alarm == "POSITION_DURATION_ALERT":
                if (
                    self.alarm_level_colors[level] == top_alert_color
                    and "Position" in top_alert_text
                    and top_alert_number == number
                ):
                    return True
            else:
                if (
                    self.alarm_level_colors[level] == top_alert_color
                    and top_alert_text.replace(" ", "_").lower() == alarm.lower()
                    and top_alert_number == 1
                ):
                    return True
            return False
        except Exception:
            raise Exception(
                "Something went wrong getting the top alarm {} inside the dashboard".format(
                    alarm
                )
            )

    def no_top_alarms(self, patient_name):
        try:
            self.web_utils.find_element(
                self.specific_top_alerts_dashboard[0],
                self.specific_top_alerts_dashboard[1].format(patient_name),
                retries=2,
                log_errors=False,
            )
            return False
        except TimeoutException:
            return True

    def click_on_update_password(self):
        try:
            self.web_utils.find_element(*self.change_password_btn).click()
        except Exception:
            raise Exception("Something went wrong with the change password button")

    def set_new_password(self, password):
        try:
            new_password_field = self.web_utils.find_element(*self.new_password_field)
            new_password_field.click()
            new_password_field.send_keys(password)
        except Exception:
            raise Exception("Something went wrong setting the new password")

    def re_enter_new_password(self, re_password):
        try:
            re_enter_password_field = self.web_utils.find_element(
                *self.re_enter_password_field
            )
            re_enter_password_field.click()
            re_enter_password_field.send_keys(re_password)
        except Exception:
            raise Exception("Something went wrong re-entering the new password")

    def check_password_message(self, error_message):
        try:
            password_error_message = self.web_utils.find_element(
                self.password_error_message[0],
                self.password_error_message[1].format(error_message),
            )
            if password_error_message.is_displayed():
                return True
            else:
                return False
        except Exception:
            raise Exception(
                "Something went wrong getting the new password error message"
            )

    def click_on_manage_audio_alarm(self):
        try:
            self.web_utils.find_element(*self.manage_audio_alarm_button).click()
        except Exception:
            raise Exception("Can not find the 'Manage audio alarm' button")

    def check_alarm_status(self, status):
        try:
            if status == "deactivated":
                return True if self.web_utils.find_element(*self.audio_off) else False
            elif status == "activated":
                return True if self.web_utils.find_element(*self.audio_on) else False
        except NoSuchElementException:
            raise Exception("Can not find the alarm status")

    def get_current_alarm_status(self):
        try:
            if self.web_utils.find_element(
                *self.audio_off, retries=3, log_errors=False
            ).is_displayed():
                return "deactivated"
        except TimeoutException:
            try:
                if self.web_utils.find_element(*self.audio_on).is_displayed():
                    return "activated"
            except Exception:
                raise Exception("Can not get the current alarm status")

    def change_alarm_status(self, status):
        try:
            if status == "ON":
                self.web_utils.find_element(*self.settings_audio_on).click()
            elif status == "OFF":
                self.web_utils.find_element(*self.settings_audio_off).click()
        except Exception:
            raise Exception("Can not find the alarm status")

    def save_alarm_status(self):
        try:
            self.web_utils.find_element(*self.save_button).click()
        except Exception:
            raise Exception("Can not save the alarm status")

    def alarm_status_modified(self):
        try:
            self.web_utils.find_element(*self.alarm_modified)
        except Exception:
            raise Exception("Can not find the alarm modified status popup")

        try:
            self.web_utils.find_element(*self.alarm_modified_ok).click()
        except Exception:
            raise Exception(
                "Can not find the alarm modified ok button inside the popup"
            )

    def is_pause_alarm_present(self):
        try:
            return (
                True
                if self.web_utils.find_element(*self.pause_alarm_btn).is_displayed()
                else False
            )
        except Exception:
            raise Exception("Can not find the pause alarm button")

    def pause_alarm(self):
        try:
            self.web_utils.find_element(*self.pause_alarm_btn).click()
        except Exception:
            raise Exception("Can not find the pause alarm button")

    def is_alarm_paused(self):
        try:
            return (
                True
                if self.web_utils.find_element(*self.alarm_paused).is_displayed()
                else False
            )
        except Exception:
            raise Exception("Can not find the paused countdown")

    def deactivate_countdown(self):
        try:
            self.web_utils.find_element(*self.cancel_countdown).click()
        except Exception:
            raise Exception("Can not cancel the alarm countdown")

    def is_popup_password_present(self):
        try:
            return self.web_utils.find_element(*self.password_required).is_displayed()
        except Exception:
            raise Exception("Expected password popup input not found")

    def is_current_password_text_present(self):
        try:
            return self.web_utils.find_element(*self.current_password).is_displayed()
        except Exception:
            raise Exception("Current password text, not found")

    def is_change_title_present(self):
        try:
            return self.web_utils.find_element(
                *self.change_password_title
            ).is_displayed()
        except Exception:
            raise Exception("Change Password title, not found")

    def is_password_tooltip_present(self):
        try:
            new_pass = self.driver.find_element(*self.new_password_field)
            new_pass.click()
            time.sleep(1)
            text = self.driver.find_element(By.CLASS_NAME, "MuiTooltip-tooltip").text
            requirements = [
                "Your password must have:",
                "8 or more characters",
                "At least one uppercase letter",
                "At least one lowercase letter",
                "At least one number",
                "At least one special character",
            ]
            text_split = text.split("\n")
            for index, requirement in enumerate(requirements):
                assert requirement == text_split[index], (
                    "Expected " + requirement + " current " + text_split[index]
                )
        except Exception:
            raise Exception("Can not find the password tooltip information")

    def password_is_required(self):
        try:
            return (
                self.driver.find_element(By.TAG_NAME, "form")
                .find_element(*self.password_required_at_change)
                .is_displayed()
            )
        except Exception:
            raise Exception("Can not find the password is required message")

    def continue_in_change_password_status(self):
        try:
            return (
                self.driver.find_element(By.TAG_NAME, "form")
                .find_element(*self.confirm_btn_password_status)
                .is_enabled()
            )
        except Exception:
            raise Exception("Can not find the Continue Button")

    def click_on_second_password_field(self):
        try:
            re_enter_password_field = self.web_utils.find_element(
                *self.re_enter_password_field
            )
            re_enter_password_field.click()
            time.sleep(1)
        except Exception:
            raise Exception("Something went wrong clicking in the second field")

    def click_on_bed(self, bed_name):
        try:
            time.sleep(3)
            self.web_utils.find_element(*self.multi_patient_view, log_errors=False).find_element(By.TAG_NAME, 'div').click()
            self.web_utils.find_element(By.XPATH, f"//h2[text()='Bed ID {bed_name}']", log_errors=False)
        except Exception:
            try:
                self.web_utils.find_element(By.XPATH, f"//h2[text()='Bed ID {bed_name}']", log_errors=False)
                logging.info('Already inside the selected bed detail')
            except Exception:
                raise Exception('Something went wrong clicking on created bed')

    def is_message_present(self, message):
        try:
            if message == 'Admit and Monitor Patient':
                message_title = self.web_utils.find_element(self.dashboard_bed_message_search[0], self.dashboard_bed_message_search[1].format(message), retries=50, log_errors=False)
            else:
                message_title = self.web_utils.find_element(self.dashboard_bed_message[0], self.dashboard_bed_message[1].format(message), retries=50, log_errors=False)
            return True if message_title.is_displayed() else False
        except Exception:
            raise Exception(f'Can not find the {message} message')

    def identify_bed(self, index):
        try:
            return self.web_utils.find_elements(*self.multi_patient_view_beds)[index].find_element(By.TAG_NAME, 'p').text
        except Exception:
            raise Exception(f'Canot identify bed {index}')

    def dismiss_modal(self):
        try:
            self.web_utils.find_element(*self.dismiss_modal_btn).click()
        except Exception:
            raise Exception('Can not get the dismiss modal button')

    def is_audio_message_popup(self):
        try:
            self.web_utils.find_element(*self.audio_password_popup_info).click()
        except Exception:
            raise Exception('Can not get the audio message information')

    def close_bed_detail_modal(self):
        try:
            self.web_utils.find_element(*self.dismiss_modal_btn).click()
        except Exception:
            raise Exception('Can not close the bed detail modal')

    def in_multipatient_view(self):
        try:
            self.web_utils.find_element(*self.multi_patient_view).click()
        except Exception:
            raise Exception('Can not close the bed detail modal')

    def is_audio_off_signal_present(self):
        try:
            audio_signal = self.web_utils.find_element(*self.audio_off_at_bedside, retries=20, log_errors=False)
            return True if audio_signal.is_displayed() else False
        except TimeoutException:
            return False
        except Exception as e:
            raise Exception(f'Can not find the audio off-signal {e}')
