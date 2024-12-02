from behave import *
from django.urls import reverse

from features.DTOs.privileges import PrivilegePaginationDTO
from features.factories.privilege_factories import PrivilegeFactory


@step("a list of user groups exist")
def step_impl(context):
    context.group_batch_size = 15
    PrivilegeFactory.create_batch(context.group_batch_size)


@step("there are no user groups")
def step_impl(context):
    context.group_batch_size = 0


@when("request the list of user groups")
def step_impl(context):
    group_list_url = reverse("group-list")
    access_token = context.user_session.access
    context.response = context.test.client.get(
        group_list_url, headers={"Authorization": f"Bearer {access_token}"}
    )


@step("the list of user groups data is correct")
def step_impl(context):
    group_list = PrivilegePaginationDTO(**context.response.data)
    assert group_list.count == (context.group_batch_size + 1)  # created groups + admin group
