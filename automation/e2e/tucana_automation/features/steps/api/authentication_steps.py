import json
import time
import uuid

from behave import *
from faker import Faker

from features.steps.api.common_api_steps import (
    valid_user_credentials,
    verify_delete_request_status,
)
from utils.api_utils import (
    requests_delete,
    requests_delete_batch,
    requests_get,
    requests_post,
    requests_put,
)


@step("A request to logout with valid password")
def request_logout(context):
    context.data = {
        "url": "/web/auth/token/logout",
        "json": {"password": context.env_config["password"]},
    }


@step("the request is made to logout")
@step("the request is made to refresh token")
@step("the request is made to update the password")
def send_request(context):
    url = context.data["url"]
    context.response = requests_post(context, url, context.data["json"], headers=None)


@step("A request to logout with invalid credentials")
def request_logout(context):
    faker = Faker()
    context.invalid_password = faker.password(
        length=10, special_chars=True, digits=True, upper_case=True, lower_case=True
    )
    context.data = {
        "url": "/web/auth/token/logout",
        "json": {"password": context.invalid_password},
    }


@step(
    "the user is informed that the session has not been logged out due to invalid password"
)
def verify_active_session(context):
    session_status = context.response.json()
    assert (
        "Unauthorized" in session_status["detail"]
    ), "Session closed with an invalid password"


@step("A request to update the password with a numeric password")
def request_update_password(context):
    faker = Faker()
    context.invalid_password = faker.bothify("##########")
    context.data = {
        "url": "/web/auth/change-password",
        "json": {"current": context.invalid_password, "new": context.invalid_password},
    }


@step("the user is told their password is too common")
def verify_password_common(context):
    password_status = context.response.json()
    assert (
        "This password is too common." in password_status["msg"]
    ), "Password updated with common password"
    assert (
        "value_error.invalid_password" in password_status["type"]
    ), "Password updated with common password"


@step("the user is told their password contains only numeric characters")
def verify_password_only_numeric_characters(context):
    password_status = context.response.json()
    assert (
        "This password is entirely numeric." in password_status["msg"]
    ), "Password updated with numeric characters only"
    assert (
        "value_error.invalid_password" in password_status["type"]
    ), "Password updated with numeric characters only"


@step("A request to update the password with the username as the password")
def request_update_password(context):
    faker = Faker()
    context.invalid_password = faker.bothify("admin###")
    context.data = {
        "url": "/web/auth/change-password",
        "json": {"current": context.invalid_password, "new": context.invalid_password},
    }


@step("the user is told their password is too similar to the username")
def verify_password_common(context):
    password_status = context.response.json()
    assert (
        "The password is too similar to the username." in password_status["msg"]
    ), "Password updated with the username in the password"
    assert (
        "value_error.invalid_password" in password_status["type"]
    ), "Password updated with the username in the password"


@step(
    "A request to update the password with a password with fewer characters than the minimum requested"
)
def request_update_password(context):
    context.invalid_password = "new"
    context.data = {
        "url": "/web/auth/change-password",
        "json": {"current": context.invalid_password, "new": context.invalid_password},
    }


@step("the user is told their password is too short")
def verify_password_short(context):
    password_status = context.response.json()
    assert (
        "This password is too short. It must contain at least 4 characters."
        in password_status["msg"]
    ), "Password updated with a very short password"
    assert (
        "value_error.invalid_password" in password_status["type"]
    ), "Password updated with a very short password"


@step("A request to refresh token with a valid refresh token")
def request_refresh_token(context):
    context.data = {
        "url": "/web/auth/token/refresh",
        "json": {"refresh": context.refresh_token},
    }


@step("the user is informed that the new access token is available")
def verify_password_common(context):
    new_access_token = context.response.json()
    assert "access" in new_access_token, "The access token is not present in response"


@step("A request to refresh token with an invalid refresh token")
def request_refresh_token(context):
    context.refresh_token = "eyJhbGciOiJSUzI1NiIsInR5cCI6IkpXVCJ9.eyJ0b2tlbl90eXBlIjoiYWNjZXNzIiwiZXhwIjoxNjg0NjE3OTg1LCJpYXQiOjE2ODQ1MzE1ODUsImp0aSI6ImY1ZjUxYzQxYmJkNzRhYzViYTQ5ODAyYzQxNzQyYmZmIiwidXNlcl9pZCI6IjdiNTVlZmIyLWE3NjctNGQ5Yy1iNzc3LWQ1NjY3NTc0NjJkNiIsInVzZXJuYW1lIjoiYWRtaW5Ac2liZWxoZWFsdGguY29tIiwiZ3JvdXBzIjpbImFkbWluIl0sImF1ZCI6InR1Y2FuYSJ9.YknuyOLqwKcJyU0CvzROuAR7e8faljdNvnoYjJP6HDhw_oDVHUktQmVGEL1ah_sApLHVz0j3RH9eHkHc4DEtDpa5y8CZAB3aY4q7RfK9D7O6rD_45UAR1ilKgPV6T-POsTcZqME7nKck6k1K0ajaSVsxTODC8fZuId5l4-i2gg56iiVJPSgz72xCYzbLlVdWT2Be3sF6M65otCk2mbAj3VAwJXFXSYD6vc5k6tSCv-DjyzguiUv-ZubAxPgO-WLWZF2-eChAjr9hialmSYoUa49hCZmaJ3s8GrhQD4HJ6qdSHL_OjpIxJgMJhKY4eYGNCdOKQvPQdAWJTmWSPUqIcc"
    context.data = {
        "url": "/web/auth/token/refresh",
        "json": {"refresh": context.refresh_token},
    }


@step('A request to update the password with a common password "{common_password}"')
def request_update_common_password(context, common_password):
    context.invalid_password = common_password
    context.data = {
        "url": "/web/auth/change-password",
        "json": {"current": context.invalid_password, "new": context.invalid_password},
    }
