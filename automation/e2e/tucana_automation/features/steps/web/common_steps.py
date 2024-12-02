import time
import datetime
from zoneinfo import ZoneInfo
from behave import step

from features.pages.bed_management_page import BedManagementPage
from features.pages.dashboard_page import DashboardPage
from features.pages.group_management_page import GroupManagementPage
from features.pages.landing_page import LandingPage


@step("Tom goes to {app_name} Web APP login page")
def open_andromeda_app(context, app_name):
    context.execute_steps(
        """
        Given a browser
    """
    )
    context.browser.driver.maximize_window()
    app_url = context.env_config["app_url"]
    landing_page = LandingPage(context.browser.driver, app_url)
    landing_page.open_app()
    context.current_page = landing_page
    assert app_url in landing_page.get_current_url()


@step("Tom logs in with his credentials")
def logs_in(context):
    context.current_page.logs_in(
        context.env_config["username"], context.env_config["password"]
    )


@step("Tom sees the dashboard")
def dashboard_present(context):
    context.current_page = DashboardPage(context.browser.driver)
    assert (
        context.current_page.is_anne_logo_present()
    ), "Can not find the dashboard page"
    assert (
        context.env_config["app_url"] + "home" == context.current_page.get_current_url()
    ), (
        "Expected page "
        + context.env_config["app_url"]
        + "home"
        + " current one "
        + context.current_page.get_current_url()
    )


@step("Tom goes to settings")
def go_to_settings(context):
    context.current_page.go_to_settings()


@step("Tom clicks on log out")
def log_out(context):
    context.current_page.log_out()


@step("Tom logs in with incorrect credentials")
def incorrect_credentials(context):
    context.current_page.logs_in(context.env_config["username"], "WrongPassword")


@step("Tom logs out correctly and is redirected to the login page")
def log_out_correctly(context):
    landing_page = LandingPage(context.browser.driver, context.env_config["app_url"])
    assert landing_page.is_login_present(), "The user wasn't logged out correctly"


@step("Tom should not be able to see the dashboard")
def log_in_error(context):
    context.current_page.login_error()


@step("Tom should see the incorrect password message")
def incorrect_password(context):
    context.current_page.login_error()


@step('Tom clicks on "{}" Option')
def clicks_on_dashboard_option(context, option):
    context.current_page = DashboardPage(context.browser.driver)
    context.current_page.click_on_option(option)


@step('Tom sees the "{}" Page')
def sees_the_page(context, page):
    pages = {
        "Group Management": GroupManagementPage(context.browser.driver),
        "Bed Management": BedManagementPage(context.browser.driver),
    }
    context.current_page = pages[page]
    assert (
        context.current_page.is_title_present()
    ), "The {} was not present here".format(page)


@step("Tom fills the log out password with the correct information")
@step("Tom fills the alarm status password with the correct information")
@step("Tom fills the password information with is admin password")
def fills_password_information(context):
    context.current_page.logout_password(context.env_config["password"])


@step("Tom fills the log out password with the incorrect information")
@step("Tom fills the password information with an incorrect admin password")
@step("Tom fills the alarm status password with the incorrect information")
def fills_incorrect_password_information_logout(context):
    context.current_page.logout_password("WrongPassword")


@step("Tom should not be able to logout")
def not_logged_out(context):
    assert (
        context.current_page.log_out_incorrect_password()
    ), "The user was able to log out with an incorrect password"


@step("Tom logs out")
def full_log_out(context):
    context.current_page = DashboardPage(context.browser.driver)
    go_to_settings(context)
    log_out(context)
    fills_password_information(context)
    clicks_continue_button(context)
    log_out_correctly(context)


@step("Tom wants to update the password")
def go_to_update_password(context):
    context.current_page = DashboardPage(context.browser.driver)
    go_to_settings(context)
    context.current_page.click_on_update_password()


@step('Tom sets the new password "{}"')
def sets_new_password(context, password):
    context.current_page.set_new_password(password)


@step('Tom re-enter the new password "{}"')
def re_enter_new_password(context, password):
    context.current_page.re_enter_new_password(password)


@step("the application notifies him the password does not meet criteria")
def password_does_not_meet_criteria(context):
    assert context.current_page.check_password_message(
        "Password does not meet criteria."
    ), "Expected message 'Password does not meet criteria' wasn't present"


@step("the application notifies him the password contains only numeric characters")
def password_only_numeric_characters(context):
    assert context.current_page.check_password_message(
        "This password is entirely numeric."
    ), ("Expected message 'This " "Password is entirely " "numeric' " "wasn't present ")


@step("the application notifies him the password is too similar to the username")
def password_too_similar_username(context):
    assert context.current_page.check_password_message(
        "The password is too similar to the username."
    ), "Expected message 'Password is too similar to the username' wasn't present"


@step("the application notifies him the password is too short")
def password_too_short(context):
    assert context.current_page.check_password_message(
        "This password is too short. It must contain at least 8 characters."
    ), "Expected message 'Password is too short' wasn't present"


@step("Tom sets the new password and makes a mistake when confirming it")
def sets_new_password(context):
    password = "AcBt34TY13"
    re_enter_password = "TvBgt67HK9"
    context.current_page.set_new_password(password)
    context.current_page.re_enter_new_password(re_enter_password)


@step("the application notifies him the password does not match previous entry")
def password_does_not_match(context):
    assert context.current_page.check_password_message(
        "Password does not match previous entry."
    ), "Expected message 'Password does not match' wasn't present"


@step("the application notifies him the password was incorrect")
def password_does_not_match(context):
    assert context.current_page.check_password_message(
        "Incorrect password. Please try again."
    ), "Expected message 'Incorrect current password. Please try again wasn't present"


@step("Tom should see the Login button disabled")
def check_login_button_status(context):
    assert (
        not context.current_page.check_login_button_disabled()
    ), "The submit button is enabled, and it should not"


@step("Tom inputs his password")
def input_password(context):
    context.current_page.fill_password(context.env_config["password"])


@step("Tom should see the Login button enabled")
def login_button_enabled(context):
    assert (
        context.current_page.check_login_button_disabled()
    ), "The submit button is disabled, and it should not"


@step("Tom clicks on the Log in button")
def submit_password(context):
    context.current_page.submit_login()


@step("Tom sees the continue button is disabled")
def continue_button_status(context):
    assert (
        not context.current_page.confirm_button_status()
    ), "The continue button is enabled, and it should not"


@step("Tom sees the continue button is enabled")
def continue_button_status(context):
    assert (
        context.current_page.confirm_button_status()
    ), "The continue button is disabled, and it should not"


@step("Tom clicks on the confirm button")
def clicks_continue_button(context):
    context.current_page.click_on_confirm_button()


@step('Tom sees the "Multi-Patient View"')
def multi_patient_view_presence(context):
    assert (
        context.current_page.multi_patient_view_presence()
    ), "The current view is not the Multi patient view"


@step("Tom sees the popup message requiring the admin password")
def change_password_popup(context):
    context.current_page.is_popup_password_present()


@step("Tom sees the popup information about the audio silenced")
def popup_audio_message(context):
    context.current_page.is_audio_message_popup()


@step("Tom sees the current password input field")
def current_password_field(context):
    context.current_page.is_current_password_text_present()


@step("Tom sees the change password title")
def sees_change_title(context):
    context.current_page.is_change_title_present()


@step("Tom clicks on the new password field he sees the tooltip password criteria")
def tooltip_password_criteria(context):
    context.current_page.is_password_tooltip_present()


@step(
    'Tom clicks on the second password form and sees the "Password is required" information at the first field'
)
def password_is_required(context):
    context.current_page.click_on_second_password_field()
    assert (
        context.current_page.password_is_required()
    ), "Password is required message was not present"


@step('Tom sees the continue button in change password is "{}"')
def continue_in_change_password(context, status):
    if status == "disabled":
        assert not context.current_page.continue_in_change_password_status(), (
            "The continue button is enabled, and it " "should not "
        )
    elif status == "enabled":
        assert not context.current_page.continue_in_change_password_status(), (
            "The continue button is disabled, and " "it should not "
        )


@step('Tom sees the "{}" button')
def sees_the_button(context, button):
    assert context.current_page.is_button_present(
        button
    ), "The {} was not present here".format(button)


@step("Tom clicks on close modal button")
def close_modal(context):
    context.current_page.click_on_close_modal()


@step(
    "Tom sees the message regarding a bed ID not being assigned to all patient monitors in the required "
    "confirmation pop-up window"
)
def confirmation_required_description_present(context):
    assert context.current_page.is_confirmation_required_description_present()


@step('Tom sees the organization name "{}" on page')
def sees_the_organization_name(context, organization_name):
    assert context.current_page.is_organization_name_present(
        organization_name
    ), "The {} was not present here".format(organization_name)


@step("Tom sees the date and time on page")
def sees_the_date_time_on_page(context):
    now = datetime.datetime.now(ZoneInfo("America/Chicago")).strftime(
        "%Y-%m-%d | %H:%M"
    )
    time.sleep(1)
    assert context.current_page.is_date_time_present(
        now
    ), "The {} was not present here".format(now)


@step('Tom sees the version number of the application')
def sees_the_organization_name(context):
    assert context.current_page.is_application_version_present(), "The version number of the application was not " \
                                                                  "present "


@step("Tom waits {} seconds")
def user_waits(context, seconds):
    time.sleep(int(seconds))


@step("Tom sees the incorrect password message")
def incorrect_password_message(context):
    assert context.current_page.is_incorrect_password_message_present()


@step("Tom verifies the Log in title style")
def verify_login_title_style(context):
    assert context.current_page.check_log_in_title_style()


@step("Tom verifies the Log in button style")
def verify_login_button_style(context):
    assert context.current_page.check_log_in_button_style()


@step("Tom verifies the Log in description style")
def verify_login_description_style(context):
    assert context.current_page.check_log_in_description_style()


@step("Tom verifies the Log in the new button style")
def new_button_style(context):
    assert context.current_page.check_button_enabled_style()