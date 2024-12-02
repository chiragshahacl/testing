import logging
import time

from faker import Faker
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver import ActionChains
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys

from features.pages.base_page import BasePage


class BedManagementPage(BasePage):
    bed_management_title = (By.XPATH, "//h2[text()='Bed Management']")
    step_add_bed = (By.XPATH, "//span[@data-testid='add-beds-title']")
    add_bed_button = (
        By.XPATH,
        "//span[@data-testid='add-beds-title']//parent::div//following-sibling::div",
    )
    bed_container = (By.XPATH, "//div[contains(class(),'MuiGrid-container')]")
    total_beds_available = (
        By.XPATH,
        "//span[@data-testid='add-beds-title']//parent::div//parent::div//following-sibling::div/div/div",
    )
    specific_bed = (
        By.XPATH,
        "//span[@data-testid='add-beds-title']//parent::div//parent::div//following-sibling::div/div/div[{}]",
    )
    specific_bed_input = (By.XPATH, "./div/div/div/input")
    next_btn = (By.XPATH, "//*[@data-testid='next-assign-beds']")
    bed_management = (By.XPATH, "//*[@data-testid='assign-beds-title']")
    assign_tab = (By.XPATH, "//tbody//tr[1]//td[2]//div/div")
    select_bed = (By.XPATH, "//div[@id='menu-']//li//p[text()='{}']/parent::li")
    finish_bed_setup = (By.XPATH, "//button[contains(text(),'Finish bed setup')]")
    confirm_bed_setup_btn = (By.XPATH, "//button[contains(text(),'Confirm')]")
    delete_specific_bed = (By.XPATH, "//div[@data-testid='remove-bed-{}']")
    bed_in_list = (By.XPATH, "//input[@aria-label='{}']")
    bed_names = (By.XPATH, "//input[contains(@class,'MuiInputBase-input')]")
    back_to_step_one_btn = (By.XPATH, "//button[@data-testid='back-add-beds']")
    confirmation_required_title = (By.XPATH, "//h1[text()='Confirmation required']")
    confirmation_required_description = (
        By.XPATH,
        "//h6[text()='Not all patient monitors have been assigned a bed "
        "ID. Please confirm before continuing.']",
    )
    bed_already_exist = (By.XPATH, "//span[contains(text(),'Bed ID already exists. Change or enter a new one.')]")
    add_beds_title = (By.XPATH, "//*[@data-testid='add-beds-title']")
    bed_name = (By.XPATH, "//*[@data-testid='bed-edit-{}']")
    beds_titles = (By.XPATH, "//input[contains(@data-testid,'bed-edit-')]")
    bed_limit_reached = (By.XPATH, "//h1[text()='Bed limit reached']")
    back_to_edit_btn = (By.XPATH, "//button[text()='Back to edit']")
    pm_element_in_table = (By.XPATH, "//tr[contains(@class,'MuiTableRow-root')]")
    pm_name_in_table = (By.XPATH, "//tr[contains(@class,'MuiTableRow-root')]/td/p[text()='{}']")

    def __init__(self, driver):
        super().__init__(driver)
        self.page_loading_time = time.time() - self.start_time

    def is_title_present(self):
        try:
            return (
                True
                if self.web_utils.find_element(
                    *self.bed_management_title
                ).is_displayed()
                else False
            )
        except Exception:
            raise Exception("Can not find the Bed Management Title")

    def get_bed_qty(self):
        try:
            add_beds_title = self.web_utils.find_element(*self.step_add_bed)
            return len(
                add_beds_title.find_elements(
                    By.XPATH,
                    "./parent::div//parent::div//following-sibling::div/div/div",
                )
            )
        except Exception:
            raise Exception("Can not get the bed qty")

    def add_new_bed(self):
        try:
            self.web_utils.find_element(*self.add_bed_button).click()
        except Exception:
            raise Exception("Can not click on the add Bed Management button")

    def is_add_new_bed_btn_available(self):
        try:
            return (
                True
                if self.web_utils.find_element(*self.add_bed_button).is_displayed()
                else False
            )
        except Exception:
            raise Exception("The add Bed Management button wasn't present")

    def set_bed_name(self, bed_position, bed_name):
        try:
            bed = self.web_utils.find_element(
                self.specific_bed[0], self.specific_bed[1].format(bed_position)
            )
            bed_input = bed.find_element(*self.specific_bed_input)
            time.sleep(1)
            bed_input.send_keys(Keys.CONTROL + "a", Keys.BACKSPACE)
            bed_input.send_keys(bed_name)
        except Exception as e:
            raise Exception(f"Can not set the Bed name {e}")

    def get_bed_name(self, bed_position):
        try:
            bed = self.web_utils.find_element(
                self.specific_bed[0], self.specific_bed[1].format(bed_position)
            )
            bed_name = bed.find_element(*self.specific_bed_input).get_attribute("value")
            return bed_name
        except Exception:
            raise Exception("Can not get the Bed name")

    def click_on_next(self):
        try:
            self.web_utils.find_element(*self.next_btn).click()
        except Exception:
            raise Exception("Can not get the next button")

    def is_bed_management_present(self):
        try:
            bed_management_title = self.web_utils.find_element(*self.bed_management)
            return True if bed_management_title.is_displayed() else False
        except Exception:
            raise Exception("Can not get the STEP 2")

    def save_monitor_bed(self, context):
        try:
            context.bed_id_monitor_one = self.web_utils.find_element(
                *self.assign_tab
            ).text
        except Exception as e:
            raise Exception(f"Can not get the bed id associated to the PM {e}")

    def assign_monitor_to_bed(self, bed_name):
        try:
            assign_bed = self.web_utils.find_element(*self.assign_tab)
            action = ActionChains(self.web_utils.driver)
            action.move_to_element(assign_bed).pause(2).click(assign_bed).pause(2).perform()
            bed = self.web_utils.find_element(self.select_bed[0], self.select_bed[1].format(bed_name))
            self.web_utils.driver.execute_script("arguments[0].scrollIntoView();", bed)
            time.sleep(2)
            self.web_utils.driver.execute_script("arguments[0].click();", bed)
        except Exception:
            raise Exception(
                "Can not set the {} to the patient monitor".format(bed_name)
            )

    def is_finish_setup_enabled(self):
        try:
            return (
                True
                if self.web_utils.find_element(*self.finish_bed_setup).is_enabled()
                else False
            )
        except Exception:
            raise Exception("Can not finished bed setup")

    def finish_setup(self):
        try:
            self.web_utils.find_element(*self.finish_bed_setup, log_errors=False).click()
        except Exception:
            raise Exception("Can not find the finish setup button")

    def confirm_bed_setup(self):
        try:
            self.web_utils.find_element(*self.confirm_bed_setup_btn, log_errors=False).click()
        except Exception:
            raise Exception("Can not find the confirmation popup")

    def delete_bed(self, bed_name):
        try:
            position = None
            for index, bed in enumerate(self.web_utils.find_elements(*self.bed_names)):
                if bed.get_attribute("value") == bed_name:
                    position = index + 1
                    break
            self.web_utils.find_element(
                self.delete_specific_bed[0],
                self.delete_specific_bed[1].format(str(position)),
            ).click()
        except Exception:
            raise Exception("Can not delete the {} bed".format(bed_name))

    def bed_still_listed(self, bed_name):
        try:
            return (
                True
                if self.web_utils.find_element(
                    self.bed_in_list[0],
                    self.bed_in_list[1].format(bed_name),
                    retries=5,
                    log_errors=False,
                ).is_displayed()
                else False
            )
        except Exception:
            return False

    def back_to_step_one(self):
        try:
            self.web_utils.find_element(*self.back_to_step_one_btn).click()
        except Exception:
            raise Exception("Can not find the back to step one button")

    def is_confirmation_required_title_present(self):
        try:
            return (
                True
                if self.web_utils.find_element(
                    *self.confirmation_required_title
                ).is_displayed()
                else False
            )
        except Exception:
            raise Exception("Can not find the confirmation required Title")

    def is_confirmation_required_description_present(self):
        try:
            return (
                True
                if self.web_utils.find_element(
                    *self.confirmation_required_description
                ).is_displayed()
                else False
            )
        except Exception:
            raise Exception("Can not find the confirmation required description")

    def verify_beds_qty_and_names(self, beds_list):
        total_beds_api = len(beds_list['resources'])
        try:
            full_title = self.web_utils.find_element(*self.add_beds_title).text
            bed_number = full_title[full_title.find("(")+1:full_title.find(")")]
        except Exception:
            raise Exception('Can not find bed qty number')
        beds_names_web = []
        try:
            for i in range(total_beds_api):
                bed_name_in_list = self.web_utils.find_element(self.bed_name[0], self.bed_name[1].format(str(i+1))).get_attribute('value')
                beds_names_web.append(bed_name_in_list)

            for i in range(total_beds_api):
                if not beds_list['resources'][i]['name'] in beds_names_web:
                    return False
                else:
                    logging.info(f"{beds_list['resources'][i]['name']} Found")

            if int(bed_number) != total_beds_api:
                logging.info(f'Expected total beds {total_beds_api} current {bed_number}')
                return False

            return True
        except Exception:
            raise Exception('Can not get bed information')

    def complete_beds_list(self, bed_limits):
        faker = Faker()
        beds_names = []
        try:
            current_beds_qty = len(self.web_utils.find_elements(*self.beds_titles))
            for i in range(bed_limits - current_beds_qty):
                self.add_new_bed()
                bed_name = faker.bothify("BQA-BL-##-###-##")
                self.set_bed_name(current_beds_qty + (i+1), bed_name)
                beds_names.append(bed_name)
            return beds_names
        except Exception:
            raise Exception('Can not find bed qty number')

    def is_bed_limit_popup_present(self):
        try:
            popup_title = self.web_utils.find_element(*self.bed_limit_reached)
            return popup_title.is_displayed()
        except Exception:
            raise Exception('Can not find the Bed Limit popup')

    def close_bed_limit_popup(self):
        try:
            self.web_utils.find_element(*self.back_to_edit_btn).click()
        except Exception:
            raise Exception('Can not close the Bed Limit Popup')

    def delete_all_created_beds(self, beds_names):
        try:
            for bed_name in beds_names:
                self.delete_bed(bed_name)
        except Exception:
            raise Exception('Something went wrong deleting creating beds')

    def current_pm_qty(self):
        try:
            return len(self.web_utils.find_elements(*self.pm_element_in_table))-1
        except Exception:
            raise Exception('Can not get the total PM qty')

    def is_pm_listed(self, pm_name):
        try:
            pm_listed = self.web_utils.find_element(self.pm_name_in_table[0], self.pm_name_in_table[1].format(pm_name))
            return True if pm_listed.is_displayed() else False
        except Exception:
            return False
