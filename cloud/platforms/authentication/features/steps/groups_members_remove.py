from authentication.users.signals import USER_REMOVED_FROM_GROUP
from behave import *
from django.urls import reverse

from features.factories.user_factories import RegularUserFactory


@step("there is a member of the group")
def step_impl(context):
    context.member_user = RegularUserFactory()
    context.new_group.members.add(context.member_user)


@when("the logged in user removes the user from the group")
def step_impl(context):
    member_detail_url = reverse(
        "member-detail",
        kwargs={"group_pk": context.new_group_id, "pk": context.member_user.id},
    )
    access_token = context.user_session.access
    context.response = context.test.client.delete(
        member_detail_url,
        headers={"Authorization": f"Bearer {access_token}"},
    )


@step("the member id is invalid")
def step_impl(context):
    context.member_user.id = context.fake.uuid4()


@step("the member removed event is logged")
def step_impl(context):
    context.publisher_mock.notify.assert_called_with(
        str(context.new_group_id), USER_REMOVED_FROM_GROUP, context.user.id
    )
