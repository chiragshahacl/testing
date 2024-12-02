from authentication.users.signals import USER_ADDED, USER_REMOVED, USER_UPDATED
from behave import *
from django.contrib.auth import get_user_model
from django.urls import reverse

from features.DTOs.users import UserDTO, UserPaginationDTO
from features.factories.user_factories import AdminUserFactory, RegularUserFactory

User = get_user_model()


@step("a valid admin user exists")
def step_impl(context):
    context.raw_password = context.fake.password()
    context.user = AdminUserFactory(password=context.raw_password)


@when("the logged in user creates a new regular user")
def step_impl(context):
    user_list_url = reverse("user-list")
    access_token = context.user_session.access
    context.new_user_raw_password = context.request.get("password")
    context.response = context.test.client.post(
        user_list_url,
        context.request,
        headers={"Authorization": f"Bearer {access_token}"},
    )


@step("the user is created")
def step_impl(context):
    new_user_data = context.response.data
    new_user_dto = UserDTO(**new_user_data)
    context.new_user = User.objects.get(id=new_user_dto.id)


@step("the new user can request to login")
def step_impl(context):
    token_obtain_url = reverse("token_obtain_pair")
    data = {
        "username": context.new_user.username,
        "password": context.new_user_raw_password,
    }
    context.response = context.test.client.post(token_obtain_url, data)


@when("request for another user details")
def step_impl(context):
    another_user = RegularUserFactory()
    user_detail_url = reverse("user-detail", kwargs={"pk": another_user.pk})
    access_token = context.user_session.access
    context.response = context.test.client.get(
        user_detail_url, headers={"Authorization": f"Bearer {access_token}"}
    )


@step("the user data is correct")
def step_impl(context):
    UserDTO(**context.response.data)


@when("request for its user details")
def step_impl(context):
    user_detail_url = reverse("user-detail", kwargs={"pk": context.user.pk})
    access_token = context.user_session.access
    context.response = context.test.client.get(
        user_detail_url, headers={"Authorization": f"Bearer {access_token}"}
    )


@step("there are users registered")
def step_impl(context):
    context.user_batch_size = 15
    RegularUserFactory.create_batch(context.user_batch_size)


@when("request the list of users")
def step_impl(context):
    user_list_url = reverse("user-list")
    access_token = context.user_session.access
    context.response = context.test.client.get(
        user_list_url, headers={"Authorization": f"Bearer {access_token}"}
    )


@step("the list of user data is correct")
def step_impl(context):
    user_list = UserPaginationDTO(**context.response.data)
    assert user_list.count == (context.user_batch_size + 1)  # regular users + admin user


@step("a request to crate a user")
def step_impl(context):
    context.request = {
        "username": "john1994",
        "password": "john123",
        "first_name": "John",
        "last_name": "Doe",
        "email": "john.doe@test.com",
    }


@step("the `password` is not provided")
def step_impl(context):
    context.request["password"] = ""


@step("the `username` is not provided")
def step_impl(context):
    context.request["username"] = ""


@step("the user created event is logged")
def step_impl(context):
    context.publisher_mock.notify.assert_called_with(
        str(context.new_user.id), USER_ADDED, context.user.id
    )


@when("request to delete the user")
def step_impl(context):
    group_detail_url = reverse("user-detail", kwargs={"pk": context.user.id})
    access_token = context.user_session.access
    context.response = context.test.client.delete(
        group_detail_url, headers={"Authorization": f"Bearer {access_token}"}
    )


@step("the user is deleted")
def step_impl(context):
    assert not (User.objects.filter(pk=context.user.id).exists())


@step("the user deleted event is logged")
def step_impl(context):
    context.publisher_mock.notify.assert_called_with(
        str(context.user.id), USER_REMOVED, str(context.user.id)
    )


@step("a request to update a user")
def step_impl(context):
    context.new_user_email = context.fake.unique.ascii_email()
    context.request = {
        "email": context.new_user_email,
    }


@when("the logged in user updates the user")
def step_impl(context):
    group_detail_url = reverse("user-detail", kwargs={"pk": context.user.id})
    access_token = context.user_session.access
    context.response = context.test.client.patch(
        group_detail_url,
        context.request,
        content_type="application/json",
        headers={"Authorization": f"Bearer {access_token}"},
    )


@step("the user is updated")
def step_impl(context):
    updated_user_data = context.response.data
    updated_user_dto = UserDTO(**updated_user_data)
    assert updated_user_dto.email == context.new_user_email


@step("the user updated event is logged")
def step_impl(context):
    context.publisher_mock.notify.assert_called_with(
        str(context.user.id), USER_UPDATED, context.user.id
    )
