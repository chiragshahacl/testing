from datetime import datetime, timedelta

import jwt
from authentication.users.models import Privilege

# from django.contrib.auth.models import User
from authentication.users.signals import USER_LOCKED, USER_LOGIN, USER_LOGOUT
from behave import *
from django.conf import settings
from django.urls import reverse
from faker import Faker
from rest_framework import status

from features.DTOs.auth import DecodedTokenDTO, RefreshedSessionDTO, SessionDTO
from features.factories.privilege_factories import PrivilegeFactory
from features.factories.user_factories import RegularUserFactory, User


@given("the app is running")
def step_impl(context):
    context.fake = Faker()


@step("a valid user exists")
def step_impl(context):
    context.raw_password = context.fake.password()
    context.user = RegularUserFactory(password=context.raw_password)


@step("the user has `admin` permissions")
def step_impl(context):
    context.user.is_superuser = True
    context.user.save()


@when("the user requests to login")
def login_user(context):
    token_obtain_url = reverse("token_obtain_pair")
    data = {"username": context.user.username, "password": context.raw_password}
    context.response = context.test.client.post(token_obtain_url, data)


@then("the request is successful")
def step_impl(context):
    assert status.is_success(context.response.status_code)


@then("the request fails")
def step_impl(context):
    assert status.is_client_error(context.response.status_code)


@step("the user gets a valid session")
def get_valid_session(context):
    context.user_session = SessionDTO(**context.response.data)
    access_token = context.user_session.access

    decoded_access = jwt.decode(
        access_token,
        settings.SIMPLE_JWT.get("VERIFYING_KEY"),
        audience=settings.SIMPLE_JWT.get("AUDIENCE"),
        algorithms=[settings.SIMPLE_JWT.get("ALGORITHM")],
    )
    DecodedTokenDTO(**decoded_access)


@step("the user gets a valid refreshed session")
def step_impl(context):
    context.user_session = RefreshedSessionDTO(**context.response.data)
    access_token = context.user_session.access

    decoded_access = jwt.decode(
        access_token,
        settings.SIMPLE_JWT.get("VERIFYING_KEY"),
        audience=settings.SIMPLE_JWT.get("AUDIENCE"),
        algorithms=[settings.SIMPLE_JWT.get("ALGORITHM")],
    )
    DecodedTokenDTO(**decoded_access)


@when("the user requests to login with an incorrect username")
def step_impl(context):
    token_obtain_url = reverse("token_obtain_pair")
    data = {
        "username": f"wrong-{context.user.username}",
        "password": context.raw_password,
    }
    context.response = context.test.client.post(token_obtain_url, data)


@when("the user requests to login with an incorrect password")
def step_impl(context):
    token_obtain_url = reverse("token_obtain_pair")
    data = {
        "username": context.user.username,
        "password": f"invalid-{context.raw_password}",
    }
    context.response = context.test.client.post(token_obtain_url, data)


@step("the user is already authenticated")
def step_impl(context):
    context.test.client.force_login(context.user)
    login_user(context)
    get_valid_session(context)


@when("the user requests a new token")
def step_impl(context):
    token_refresh_url = reverse("token_refresh")
    refresh_token = context.user_session.refresh
    data = {"refresh": refresh_token}
    context.response = context.test.client.post(token_refresh_url, data)


@when("the user logs out")
def step_impl(context):
    token_log_out_url = reverse("token_logout")
    access_token = context.user_session.access
    context.response = context.test.client.post(
        token_log_out_url,
        context.request,
        headers={"Authorization": f"Bearer {access_token}"},
    )


@step("the user is not authenticated")
def step_impl(context):
    context.test.client.logout()
    context.user_session = SessionDTO(access="", refresh="")


@step("the user is a member of groups")
def step_impl(context):
    context.group_batch_size = 15
    context.group_users = PrivilegeFactory.create_batch(context.group_batch_size)

    for group in context.group_users:
        group.members.add(context.user)


@step("the login event is logged")
def step_impl(context):
    context.publisher_mock.notify.assert_called_with(
        str(context.user.id), USER_LOGIN, context.user.id
    )


@step("the logout event is logged")
def step_impl(context):
    context.publisher_mock.notify.assert_called_with(
        str(context.user.id), USER_LOGOUT, context.user.id
    )


@step("a request to log out")
def step_impl(context):
    context.request = {
        "password": context.raw_password,
    }


@step("the password is empty")
def step_impl(context):
    context.request = {}


@step("the password is incorrect")
def step_impl(context):
    context.request["password"] = f"{context.fake.password()}-invalid"


@step("the user account is locked")
def step_impl(context):
    context.user.blocked_until = datetime.now() + timedelta(
        minutes=settings.AUTHENTICATION_ACCOUNT_LOCKOUT_IN_MINUTES
    )
    context.user.save()


@when("the user requests to login with an incorrect password as many times as possible")
def step_impl(context):
    token_obtain_url = reverse("token_obtain_pair")
    data = {
        "username": context.user.username,
        "password": f"invalid-{context.raw_password}",
    }
    for _ in range(settings.AUTHENTICATION_FAILURE_THRESHOLD + 1):
        context.response = context.test.client.post(token_obtain_url, data)


@step("the account locked event is logged")
def step_impl(context):
    context.publisher_mock.notify.assert_called(), "Not was called."
    (
        context.publisher_mock.notify.assert_called_with(
            str(context.user.id), USER_LOCKED, "system"
        ),
        "Not was called with these params.",
    )


@step("the account is locked")
def step_impl(context):
    context.user.refresh_from_db()
    assert context.user.blocked_until


@given('a valid user with group "{}" exists')
def step_impl(context, group):
    context.raw_password = context.fake.password()
    context.user = RegularUserFactory(password=context.raw_password)
    group_name, _ = Privilege.objects.get_or_create(name=group)
    context.user.privileges.set([group_name])


@step('the user group "{}" is in the token')
def get_valid_group(context, group):
    context.user_session = SessionDTO(**context.response.data)
    access_token = context.user_session.access

    decoded_access = jwt.decode(
        access_token,
        settings.SIMPLE_JWT.get("VERIFYING_KEY"),
        audience=settings.SIMPLE_JWT.get("AUDIENCE"),
        algorithms=[settings.SIMPLE_JWT.get("ALGORITHM")],
    )
    DecodedTokenDTO(**decoded_access)
    groups = decoded_access.get("groups", [])
    assert group in groups, f"Group {group} not found in token groups {groups}"
