from authentication.users.models import Privilege
from authentication.users.signals import GROUP_ADDED
from behave import *
from django.urls import reverse

from features.DTOs.privileges import PrivilegeDTO
from features.factories.privilege_factories import PrivilegeFactory


@step("a request to create a user group")
def step_impl(context):
    context.new_group_name = context.fake.unique.word()
    context.request = {
        "name": context.new_group_name,
    }


@when("the logged in user creates a new user group")
def step_impl(context):
    group_list_url = reverse("group-list")
    access_token = context.user_session.access
    context.response = context.test.client.post(
        group_list_url,
        context.request,
        headers={"Authorization": f"Bearer {access_token}"},
    )


@step("the user group is created")
def step_impl(context):
    new_group_data = context.response.data
    new_group_dto = PrivilegeDTO(**new_group_data)
    assert new_group_dto.name == context.new_group_name
    context.new_group = Privilege.objects.get(id=new_group_dto.id)


@step("the group name is empty")
def step_impl(context):
    context.request["name"] = ""


@step("the group name is already taken")
def step_impl(context):
    PrivilegeFactory(name=context.new_group_name)


@step("the group created event is logged")
def step_impl(context):
    context.publisher_mock.notify.assert_called_with(
        str(context.new_group.id), GROUP_ADDED, context.user.id
    )
