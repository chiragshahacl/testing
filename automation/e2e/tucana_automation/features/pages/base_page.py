import time

from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.common.by import By

from .web_utils import WebUtils


class BasePage:
    page_loading_time = 0
    xpath_lower_text = (
        "translate(text(), 'ABCDEFGHIJKLMNOPQRSTUVWXYZ', 'abcdefghijklmnopqrstuvwxyz')"
    )
    xpath_lower_string = "translate(string(), 'ABCDEFGHIJKLMNOPQRSTUVWXYZ', 'abcdefghijklmnopqrstuvwxyz')"
    alarm_level_colors = {
        "HI": "#ff4c42",
        "ME": "#f6c905",
        "LO": "#75f8fc",
        "OFF": "#0d151c",
    }
    button = (By.XPATH, "//button[contains(text(),'{}')]")
    management_close_button = (By.XPATH, "//div[@data-testid='dismiss-modal']")
    unsaved_information_title = (By.XPATH, "//h1[text()='Unsaved information']")
    unsaved_changes_title = (By.XPATH, "//h1[text()='Unsaved changes']")
    error_message = (By.XPATH, "//span[contains(text(),'{}')]")
    organization_name = (By.XPATH, "//span[contains(text(),'{}')]")
    date = (By.XPATH, "//span[contains(text(),'{}')]")
    application_version = (By.XPATH, "//*[@data-testid='sibel-version']")
    audio_alarm_popup = (By.XPATH, "//h1[text()='Audio alarm is enabled']")
    audio_alarm_popup_message = (By.XPATH, "//h6[text()='You can pause audio alarms in the navigation menu or disable audio alarms in the settings.']")
    back_to_edit_btn = (By.XPATH, "//*[@data-testid='back-to-edit-button']")
    incorrect_password = (By.XPATH, "//p[text()='Incorrect password. Please try again.']")

    def __init__(self, driver):
        self.start_time = time.time()
        self.driver = driver
        self.web_utils = WebUtils(driver)

    def get_page_loading_time(self):
        return self.page_loading_time

    def get_current_url(self):
        return self.driver.current_url

    def go_to_previous_page(self):
        return self.driver.back()

    def is_button_present(self, button_name):
        try:
            return (
                True
                if self.web_utils.find_element(
                    self.button[0],
                    self.button[1].format(button_name),
                    retries=5,
                    log_errors=False,
                ).is_displayed()
                else False
            )
        except Exception:
            raise Exception(f"Can not get the button {button_name}")

    def click_on_close_modal(self):
        try:
            self.web_utils.find_element(*self.management_close_button).click()
        except Exception:
            raise Exception("Can not get the close modal button")

    def is_unsaved_information_title_present(self):
        try:
            return (
                True
                if self.web_utils.find_element(
                    *self.unsaved_information_title
                ).is_displayed()
                else False
            )
        except Exception:
            raise Exception("Can not find the unsaved information Title")

    def is_error_message_present(self, error_message_text):
        try:
            return (
                True
                if self.web_utils.find_element(
                    self.error_message[0],
                    self.error_message[1].format(error_message_text),
                    retries=5,
                    log_errors=False,
                ).is_displayed()
                else False
            )
        except Exception:
            raise Exception(f"Can not get the error message {error_message_text}")

    def is_organization_name_present(self, organization):
        try:
            return (
                True
                if self.web_utils.find_element(
                    self.organization_name[0],
                    self.organization_name[1].format(organization),
                    retries=5,
                    log_errors=False,
                ).is_displayed()
                else False
            )
        except Exception:
            raise Exception(f"Can not get the button {organization}")

    def is_date_time_present(self, times):
        try:
            date_time = self.web_utils.find_element(self.date[0], self.date[1].format(times), retries=5, log_errors=False)
            return True if date_time.is_displayed() else False
        except Exception:
            raise Exception(f"Can not get the time and date on page")

    def is_application_version_present(self):
        try:
            return (
                True
                if self.web_utils.find_element(
                    self.application_version[0],
                    self.application_version[1],
                    retries=5,
                    log_errors=False,
                ).is_displayed()
                else False
            )
        except Exception:
            raise Exception(f"Can not get the application version")

    def click_on_unsaved_information_button(self, button_name):
        try:
            self.web_utils.find_element(
                self.button[0],
                self.button[1].format(button_name),
                retries=5,
                log_errors=False,
            ).click()
        except Exception:
            raise Exception(f"Can not get the button {button_name}")

    def page_refresh(self):
        self.web_utils.driver.refresh()
        time.sleep(5)
        try:
            audio_alarm_popup = self.web_utils.find_element(*self.audio_alarm_popup)
            if audio_alarm_popup.is_displayed():
                assert self.check_audio_alarm_message()
                self.web_utils.find_element(self.button[0], self.button[1].format('OK')).click()
        except Exception as e:
            raise Exception(f"Audio Alarm ON popup message should be present after refresh and it's not {e}")

    def check_audio_alarm_message(self):
        try:
            audio_on_popup_message = self.web_utils.find_element(*self.audio_alarm_popup_message)
            return True if audio_on_popup_message.is_displayed() else False
        except Exception:
            raise NoSuchElementException('Something went wrong with the Audio Alarm ON POPUP message')

    def back_to_edit(self):
        try:
            self.web_utils.find_element(*self.back_to_edit_btn).click()
        except Exception:
            raise Exception('Can not get the back to edit button')

    def is_incorrect_password_message_present(self):
        try:
            message = self.web_utils.find_element(*self.incorrect_password)
            return True if message.is_displayed() else False
        except Exception:
            raise Exception('Can not get the incorrect password message')

    def is_unsaved_changes_title_present(self):
        try:
            return (
                True
                if self.web_utils.find_element(
                    *self.unsaved_changes_title
                ).is_displayed()
                else False
            )
        except Exception:
            raise Exception("Can not find the unsaved changes title")
