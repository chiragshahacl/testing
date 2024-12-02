from behave import *
from django.contrib.auth import authenticate
from django.urls import reverse


@step("a request to update a the user password")
def step_impl(context):
    context.new_raw_password = f"{context.fake.password()}-new"
    context.request = {
        "current_password": context.raw_password,
        "new_password": context.new_raw_password,
    }


@when("the logged in user updates the user password")
def step_impl(context):
    change_password_url = reverse("change_password")
    access_token = context.user_session.access
    context.response = context.test.client.post(
        change_password_url,
        context.request,
        content_type="application/json",
        headers={"Authorization": f"Bearer {access_token}"},
    )


@step("the user password is updated")
def step_impl(context):
    assert (
        authenticate(username=context.user.username, password=context.new_raw_password) is not None
    )


@step("the new password is empty")
def step_impl(context):
    context.request.pop("new_password")


@step("the user password is not updated")
def step_impl(context):
    assert authenticate(username=context.user.username, password=context.raw_password) is not None


@step("the current password is empty")
def step_impl(context):
    context.request.pop("current_password")


@step("the current password is incorrect")
def step_impl(context):
    context.request["current_password"] = f"{context.fake.password()}-invalid"


@step("the new password is too short")
def step_impl(context):
    context.request["new_password"] = "1B$"
