from authentication.users.signals import GROUP_UPDATED
from behave import *
from django.urls import reverse

from features.DTOs.privileges import PrivilegeDTO


@step("a request to update a user group")
def step_impl(context):
    context.new_group_name = context.fake.unique.word()
    context.request = {
        "name": context.new_group_name,
    }


@when("the logged in user updates the created user group")
def step_impl(context):
    group_detail_url = reverse("group-detail", kwargs={"pk": context.new_group_id})
    access_token = context.user_session.access
    context.response = context.test.client.patch(
        group_detail_url,
        context.request,
        content_type="application/json",
        headers={"Authorization": f"Bearer {access_token}"},
    )


@step("the user group is updated")
def step_impl(context):
    group_updated_data = context.response.data
    group_updated_dto = PrivilegeDTO(**group_updated_data)
    assert group_updated_dto.name == context.new_group_name


@step("the group updated event is logged")
def step_impl(context):
    context.publisher_mock.notify.assert_called_with(
        str(context.new_group.id), GROUP_UPDATED, context.user.id
    )
