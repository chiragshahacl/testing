import logging
import time

from selenium.webdriver.common.by import By
from features.pages.base_page import BasePage
from selenium.webdriver.support.color import Color


class LandingPage(BasePage):
    log_in_title = (By.XPATH, "//h1[text()='Log in']")
    user_name = (By.XPATH, "//input[@name='username']")
    user_password = (By.XPATH, "//input[@name='password']")
    log_in_btn = (By.XPATH, "//*[@data-testid='login-button']")
    login_error_msg = (
        By.XPATH,
        "//span[text()='Incorrect password. Please try again.']",
    )
    form = (By.XPATH, "//form")
    log_in_description = (By.XPATH, "//h6[text()='Welcome to Sibel Central Hub']")

    def __init__(self, driver, app_url):
        super().__init__(driver)
        self.login_url = app_url
        self.page_loading_time = time.time() - self.start_time

    def open_app(self):
        self.web_utils.get(self.login_url)

    def logs_in(self, user, password):
        # self.fill_user_name(user)
        self.fill_password(password)
        self.submit_login()

    def fill_user_name(self, user):
        try:
            user_name = self.web_utils.find_element(*self.user_name)
            user_name.click()
            user_name.send_keys(user)
        except Exception:
            raise Exception("Can not fill the username information")

    def fill_password(self, password):
        try:
            user_password = self.web_utils.find_element(*self.user_password)
            user_password.click()
            time.sleep(0.5)
            user_password.send_keys(password)
            time.sleep(1)
        except Exception:
            raise Exception("Can not fill the password information")

    def submit_login(self):
        try:
            self.web_utils.find_element(*self.log_in_btn).click()
        except Exception as e:
            raise Exception(f"Can not find the submit button {e}")

    def login_error(self):
        try:
            self.web_utils.find_element(*self.login_error_msg)
        except Exception:
            raise Exception("The error message pop up was not here")

    def is_login_present(self):
        try:
            login = self.web_utils.find_element(*self.log_in_title, retries=20, log_errors=False)
            return True if login.is_displayed() else False
        except Exception:
            raise Exception("The login title was not here")

    def check_login_button_disabled(self):
        try:
            button = self.web_utils.find_element(*self.form, retries=20, log_errors=False).find_element(By.XPATH,
                                                                                                        "./child::button")
            return True if button.is_enabled() else False
        except Exception:
            raise Exception("Can not find the log in button")

    def check_log_in_title_style(self):
        try:
            logging.info('Checking Log In Title Font Family, size, weight and color')
            title = self.web_utils.find_element(*self.log_in_title)
            styles = {"font_type": "Ubuntu", "font_size": "40px", "font_weight": "700", "font_color": "#ffffff"}
            return self.check_style_parameters(title,
                                        font_type=styles['font_type'],
                                        font_size=styles['font_size'],
                                        font_weight=styles['font_weight'],
                                        font_color=styles['font_color']
                                        )
        except AssertionError as e:
            raise Exception(f'{e}')

    def check_log_in_button_style(self):
        try:
            logging.info('Checking Log In Button Font Family, size, weight and color')
            button = self.web_utils.find_element(*self.form, retries=20, log_errors=False).find_element(By.XPATH, "./child::button")
            styles = {"font_type": "Ubuntu", "font_size": "24px", "font_weight": "700", "font_color": "#5c5c5c"}
            text_style = self.check_style_parameters(button,
                                        font_type=styles['font_type'],
                                        font_size=styles['font_size'],
                                        font_weight=styles['font_weight'],
                                        font_color=styles['font_color']
                                        )
            logging.info('Checking Button Background Color')
            button_style = self.check_button_background_color(status='disabled')
            return True if (text_style and button_style) else False
        except Exception as e:
            raise Exception(f'{e}')

    def check_log_in_description_style(self):
        try:
            logging.info('Checking Log In Description Font Family, size, weight and color')
            button = self.web_utils.find_element(*self.log_in_description)
            styles = {"font_type": "Open_Sans", "font_size": "21px", "font_weight": "400", "font_color": "#f2f4f6"}
            return self.check_style_parameters(button,
                                        font_type=styles['font_type'],
                                        font_size=styles['font_size'],
                                        font_weight=styles['font_weight'],
                                        font_color=styles['font_color']
                                        )
        except Exception as e:
            raise Exception(f'{e}')

    def check_button_enabled_style(self):
        try:
            logging.info('Checking Button Enabled Font Family, size, weight and color')
            button = self.web_utils.find_element(*self.form, retries=20, log_errors=False).find_element(By.XPATH, "./child::button")
            styles = {"font_type": "Ubuntu", "font_size": "24px", "font_weight": "700", "font_color": "#ffffff"}
            text_style = self.check_style_parameters(button,
                                        font_type=styles['font_type'],
                                        font_size=styles['font_size'],
                                        font_weight=styles['font_weight'],
                                        font_color=styles['font_color']
                                        )
            logging.info('Checking Button Background Color')
            button_style = self.check_button_background_color(status='enabled')
            return True if (text_style and button_style) else False
        except Exception as e:
            raise Exception(f'{e}')

    def check_button_background_color(self, status):
        try:
            button = self.web_utils.find_element(*self.form, retries=20, log_errors=False).find_element(By.XPATH, "./child::button")
            background_color = button.value_of_css_property('background-color')
            if status == 'disabled':
                if "#252829" == Color.from_string(background_color).hex:
                    return True
                else:
                    raise Exception(f'Color expected #252829 current {Color.from_string(background_color).hex}')
            else:
                if "#2188c6" == Color.from_string(background_color).hex:
                    return True
                else:
                    raise Exception(f'Color expected #2188c6 current {Color.from_string(background_color).hex}')
        except Exception as e:
            raise Exception(f'{e}')

    def check_style_parameters(self, element, font_type=None, font_size=None, font_weight=None, font_color=None):
        try:
            if font_type not in element.value_of_css_property("font-family"):
                raise Exception(
                    f"Expected font type {font_type} current {element.value_of_css_property('font-family')}")
            if font_size != element.value_of_css_property("font-size"):
                raise Exception(f"Expected font type {font_size} current {element.value_of_css_property('font-size')}")
            if font_weight != element.value_of_css_property("font-weight"):
                raise Exception(
                    f"Expected font type {font_weight} current {element.value_of_css_property('font-weight')}")
            font_color_attribute = Color.from_string(element.value_of_css_property("color")).hex
            if font_color != font_color_attribute:
                raise Exception(f"Expected font color {font_color} current {font_color_attribute}")
            return True
        except Exception as e:
            raise Exception(f'{e}')
