import logging
import random
import time

from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys

from features.pages.base_page import BasePage


class GroupManagementPage(BasePage):
    group_management_title = (By.XPATH, "//h2[text()='Group Management']")
    groups_qty = (By.XPATH, "//h2[contains(text(),'Groups (')]")
    groups_buttons = (By.ID, "list-container")
    groups_individual_buttons = (By.XPATH, "./ul/li/div/div/div/input")
    groups_add = (
        By.XPATH,
        "//h2[contains(text(),'Groups (')]//ancestor::div/parent::div/following-sibling::div/div[2]",
    )
    edit_group_name_btn = (By.XPATH, "//p[text()='Edit group name']")
    delete_group_btn = (By.XPATH, "//p[text()='Delete group']")
    beds_qty = (By.XPATH, "//h2[contains(text(),'Beds (')]")
    beds_table = (By.XPATH, "//table[contains(@class, 'MuiTable-root')]")
    beds_elements = (
        By.XPATH,
        "//h2[contains(text(),'Beds (')]/parent::div/parent::div/following-sibling::div/table/tbody/tr",
    )
    specific_bed = (
        By.XPATH,
        "//h2[contains(text(),'Beds (')]/parent::div/parent::div/following-sibling::div/table/tbody/tr[{}]/td/span",
    )
    specific_bed_tick = (By.XPATH, "./*[local-name()='svg']/*[local-name()='path']")
    bed_number = (
        By.XPATH,
        "//h2[contains(text(),'Beds (')]/parent::div/parent::div/following-sibling::div/table/tbody/tr[{}]/td[2]",
    )
    bed_uid = (
        By.XPATH,
        "//h2[contains(text(),'Beds (')]/parent::div/parent::div/following-sibling::div/table/tbody/tr[{}]/td[3]",
    )
    finish_setup_btn = (By.XPATH, "//button[text()='Finish Setup']")
    bed_name_and_uid_in_group = (
        By.XPATH,
        "//h2[contains(text(),'Groups (')]//parent::div//parent::div//parent::div//following-sibling::div//following-sibling::div//table//tbody//tr[{}]",
    )
    group_box = (By.XPATH, "//div[@id='list-container']/ul/li[{}]/div/div/div")
    group_name = (By.XPATH, "./input[contains(@type,'text')]")
    confirm_btn = (By.XPATH, "//button[text()='Confirm']")
    specific_bed_selection = (
        By.XPATH,
        "//h2[contains(text(),'Beds (')]/parent::div/parent::div/following-sibling::div/table/tbody/tr/td/p[text()='{}']/parent::td/preceding-sibling::td/span",
    )
    beds_in_groups = (
        By.XPATH,
        "//span[contains(text(), 'total')]/preceding-sibling::div/following-sibling::div/table/tbody/tr",
    )
    discard_btn = (By.XPATH, "//button[text() ='Discard']")
    close_group_modal = (By.XPATH, "//div[@data-testid ='dismiss-modal']")
    total_beds_in_group = (By.XPATH, "//span[contains(text(), 'total')]")
    confirmation_required_description_groups = (
        By.XPATH,
        "//h6[text()='Not all beds have been assigned to a group. Please "
        "confirm before continuing.']",
    )
    individual_group_box = (By.XPATH, "//input[@value='{}']/parent::div")
    total_selected_beds = (By.XPATH, "//p[contains(text(), 'Selected')]")
    group_names = (By.XPATH, "//div[@id='list-container']/ul/li/div/div/div/input")
    group_name_in_use = (By.XPATH, "//span[text() = 'Bed group name already exists. Change or enter a new one.']")

    def __init__(self, driver):
        super().__init__(driver)
        self.page_loading_time = time.time() - self.start_time

    def is_title_present(self):
        try:
            return (
                True
                if self.web_utils.find_element(
                    *self.group_management_title
                ).is_displayed()
                else False
            )
        except Exception:
            raise Exception("Can not find the Group Management Title")

    def get_groups_qty(self):
        try:
            groups = self.web_utils.find_element(*self.groups_qty).text
            return int(groups[groups.find("(") + 1 : groups.find(")")])
        except Exception:
            raise Exception("Can not get the groups quantity")

    def create_new_group(self):
        try:
            self.web_utils.find_element(*self.groups_add).click()
        except Exception:
            raise Exception("Can not add a new group")

    def is_new_group_sign_present(self):
        try:
            return (
                True
                if self.web_utils.find_element(*self.groups_add).is_displayed()
                else False
            )
        except Exception:
            raise Exception("Can not find the add new group sign")

    def get_default_group_name(self, position):
        try:
            group_box = self.web_utils.find_element_by_xpath(
                self.group_box[1].format(position)
            )
            return group_box.find_element(*self.group_name).get_attribute("value")
        except Exception:
            raise Exception("Can not get the group name")

    def delete_group(self, group_name):
        try:
            groups = self.web_utils.find_element(*self.groups_buttons).find_elements(
                *self.groups_individual_buttons
            )
            for index, group in enumerate(groups):
                if group.get_attribute("value") == group_name:
                    groups[index].find_element(By.XPATH, "../..").click()
                    break
        except Exception:
            raise Exception("Can not click on the " + group_name)
        self.web_utils.find_element(*self.delete_group_btn).click()

    def click_on_confirm(self):
        try:
            self.web_utils.find_element(*self.confirm_btn).click()
        except Exception:
            raise Exception("Can not find the confirm button")

    def wait_until_confirm_is_gone(self):
        try:
            self.web_utils.wait_element_to_hide(*self.confirm_btn)
        except Exception:
            pass

    def is_finish_setup_disabled(self):
        try:
            return (
                False
                if self.web_utils.find_elements(*self.finish_setup_btn)[0].is_enabled()
                else True
            )
        except Exception:
            raise Exception("Something went wrong with the finish setup button")

    def is_finish_setup_enabled(self):
        try:
            if self.web_utils.find_elements(*self.finish_setup_btn)[0].is_enabled():
                return True
            else:
                raise Exception("Finish setup button should be enabled")
        except Exception:
            groups = self.web_utils.find_element(*self.groups_buttons).find_elements(
                *self.groups_individual_buttons
            )
            for index, group in enumerate(groups):
                group_button = groups[index]
                group_name = group.get_attribute("value")
                group_button.find_element(By.XPATH, "../..").click()
                time.sleep(1)
                if "0" in self.web_utils.find_element(*self.total_beds_in_group).text:
                    self.delete_group(group_name)
                    logging.info(
                        "Deleted Group {} with no bed associated".format(group_name)
                    )
            time.sleep(2)
            return (
                True
                if self.web_utils.find_elements(*self.finish_setup_btn)[0].is_enabled()
                else False
            )

    def finish_setup(self):
        try:
            self.web_utils.find_elements(*self.finish_setup_btn)[0].click()
        except Exception:
            raise Exception("Can not find the finish setup button")

    def select_one_bed(self, previous=None):
        try:
            random_link = random.randint(
                2, len(self.web_utils.find_elements(*self.beds_elements))
            )
            checkbox = self.web_utils.find_element(
                self.specific_bed[0], self.specific_bed[1].format(str(random_link))
            )
            bed_name = self.web_utils.find_element_by_xpath(
                self.bed_number[1].format(str(random_link))
            ).text
            bed_uid = self.web_utils.find_element_by_xpath(
                self.bed_uid[1].format(str(random_link))
            ).text
            logging.info("{} is going to be selected".format(bed_name))
            if bed_name == previous or ("BQA" in bed_name):
                if "BQA" in bed_name:
                    logging.info(
                        "Bed {} is not selectable, trying to choose a different one".format(
                            bed_name
                        )
                    )
                else:
                    logging.info(
                        "Bed {} was already chosen, trying to choose a different one".format(
                            bed_name
                        )
                    )
                return None, None
            time.sleep(2)
            checkbox.click()
            time.sleep(1)
            try:
                checkbox.find_element(*self.specific_bed_tick)
            except Exception:
                raise Exception("The {} was not selected".format(bed_uid))
            return bed_name, bed_uid
        except Exception as e:
            raise Exception(str(e))

    def is_bed_listed(self, bed, position):
        try:
            bed_name = self.web_utils.find_element(
                self.bed_name_and_uid_in_group[0],
                self.bed_name_and_uid_in_group[1].format(position),
            ).text.split("\n")[0]
            bed_uid = self.web_utils.find_element(
                self.bed_name_and_uid_in_group[0],
                self.bed_name_and_uid_in_group[1].format(position),
            ).text.split("\n")[1]

            if bed_uid == "N/A":
                bed_uid = "-"

            if bed_name != bed[0]:
                raise Exception("Expected bed_name " + bed[0] + " current " + bed_name)

            if bed_uid != bed[1]:
                raise Exception("Expected bed_uid " + bed[1] + " current " + bed_uid)

            return True
        except Exception as e:
            raise Exception(str(e))

    def edit_group_name(self, group_name, old_name):
        try:
            groups = self.web_utils.find_element(*self.groups_buttons).find_elements(
                *self.groups_individual_buttons
            )
            group_button = None
            for index, group in enumerate(groups):
                if group.get_attribute("value") == old_name:
                    group_button = groups[index]
                    group_button.find_element(By.XPATH, "../..").click()
                    break
            time.sleep(1)
            self.web_utils.find_element(*self.edit_group_name_btn).click()
            group_button.send_keys(Keys.CONTROL, "a")
            group_button.send_keys(Keys.BACKSPACE)
            group_button.send_keys(group_name)
        except Exception as e:
            raise Exception(str(e))

    def select_specific_bed(self, bed_name):
        try:
            self.web_utils.find_element(
                self.specific_bed_selection[0],
                self.specific_bed_selection[1].format(bed_name),
            ).click()
            time.sleep(1)
        except Exception:
            raise Exception("Can not set the bed {}".format(bed_name))

    def specific_bed_in_group(self, bed_name):
        try:
            return (
                True
                if self.web_utils.find_element(
                    self.bed_name_and_uid_in_group[0],
                    self.bed_name_and_uid_in_group[1].format(1),
                ).text.split("\n")[0]
                == bed_name
                else False
            )
            time.sleep(0.5)
        except Exception:
            raise Exception(
                "Something went wrong finding the bed {} inside the group".format(
                    bed_name
                )
            )

    def save_groups_and_beds(self):
        groups = self.web_utils.find_element(*self.groups_buttons).find_elements(
            *self.groups_individual_buttons
        )
        saved_groups = {}
        for index, group in enumerate(groups):
            group_button = groups[index]
            group_name = group.get_attribute("value")
            group_button.find_element(By.XPATH, "../..").click()
            time.sleep(2)
            beds = self.web_utils.find_elements(*self.beds_in_groups)
            bed_names = []
            for bed in beds:
                bed_names.append(bed.find_element(By.XPATH, "./td").text)
            saved_groups[group_name] = bed_names

        return saved_groups

    def listed_groups(self):
        groups = self.web_utils.find_element(*self.groups_buttons).find_elements(
            *self.groups_individual_buttons
        )
        listed_groups = []
        for index, group in enumerate(groups):
            group_button = groups[index]
            group_name = group.get_attribute("value")
            group_button.find_element(By.XPATH, "../..").click()
            time.sleep(2)
            listed_groups.append(group_name)
        return listed_groups

    def get_major_index(self, listed_groups):
        group_bed_ids = []
        for group_name in listed_groups:
            if "Group" in group_name:
                group_bed_ids.append(int(group_name.split(" ")[1]))
        return max(group_bed_ids, key=int)

    def close_modal(self):
        try:
            self.web_utils.find_element(*self.close_group_modal).click()
        except Exception:
            raise Exception("Can not close the group modal")

    def discard_changes(self):
        try:
            self.web_utils.find_element(*self.discard_btn).click()
        except Exception:
            raise Exception("Can not discard the changes")

    def is_confirmation_required_description_present(self):
        try:
            return (
                True
                if self.web_utils.find_element(
                    *self.confirmation_required_description_groups
                ).is_displayed()
                else False
            )
        except Exception:
            raise Exception("Can not find the confirmation required description")

    def verify_field_outline(self, old_name):
        try:
            group_box = self.web_utils.find_element(self.individual_group_box[0], self.individual_group_box[1].format(old_name), highlight_elements=False)
            return True if 'rgb(222, 64, 56)' in group_box.get_attribute('style') else False
        except Exception:
            raise Exception('Something went wrong verifying outline field color')

    def select_beds(self, total_beds):
        try:
            beds = self.web_utils.find_elements(*self.beds_elements)
            for i in range(total_beds):
                beds[i+1].find_elements(By.XPATH, "./td")[0].click()
        except Exception:
            raise Exception('Something went wrong selecting the beds')

        try:
            total_selected = self.web_utils.find_element(*self.total_selected_beds).text
            return True if '16/16' in total_selected else False
        except Exception:
            raise Exception('Something went wrong getting the total selected beds')

    def check_checkbox_disabled(self):
        try:
            beds = self.web_utils.find_elements(*self.beds_elements)
            for i in range(18, len(beds)):
                beds[i].find_elements(By.XPATH, "./td")[0].find_element(By.XPATH, "./span[contains(@class,'Mui-disabled')]")
                logging.info(f'Bed {i} checkbox disabled')
            all_disabled = True
            return True if all_disabled else False
        except Exception:
            raise Exception('Something went wrong verifying disabled checkboxes')

    def get_groups_names(self):
        try:
            groups = self.web_utils.find_elements(*self.group_names)
            names = []
            for group in groups:
                names.append(group.get_attribute('value'))
            return names
        except Exception:
            raise Exception('Can not get the group names')

    def is_group_name_in_use(self):
        try:
            time.sleep(1)
            message = self.web_utils.find_element(*self.group_name_in_use)
            return True if message.is_displayed() else False
        except Exception:
            raise Exception('Can not get the group name in use message')
