from behave import *
from django.urls import reverse

from features.DTOs.users import UserPaginationDTO


@when("request the list of group members")
def step_impl(context):
    member_list_url = reverse("member-list", kwargs={"group_pk": context.new_group_id})
    access_token = context.user_session.access
    context.response = context.test.client.get(
        member_list_url,
        headers={"Authorization": f"Bearer {access_token}"},
    )


@step("the list of group members data is correct")
def step_impl(context):
    member_list = UserPaginationDTO(**context.response.data)
    assert member_list.count == context.user_batch_size


@step("the group has no members")
def step_impl(context):
    context.new_group.members.all().delete()
    context.user_batch_size = 0


@step("the group does not exist")
def step_impl(context):
    context.new_group_id = context.fake.uuid4()
