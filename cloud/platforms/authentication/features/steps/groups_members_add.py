from authentication.users.models import Privilege
from authentication.users.signals import USER_ADDED_TO_GROUP, USER_REMOVED_FROM_GROUP
from behave import *
from django.urls import reverse

from features.factories.user_factories import RegularUserFactory


@step("a request to add a user as group member")
def step_impl(context):
    context.member_user = RegularUserFactory()
    context.request = {"user": context.member_user.id}


@when("the logged in user adds the user to the group")
def step_impl(context):
    member_list_url = reverse("member-list", kwargs={"group_pk": context.new_group.id})
    access_token = context.user_session.access
    context.response = context.test.client.post(
        member_list_url,
        context.request,
        headers={"Authorization": f"Bearer {access_token}"},
    )


@step("the user is a group member")
def is_group_member(context):
    assert (
        Privilege.objects.get(id=context.new_group.id)
        .members.all()
        .filter(id=context.member_user.id)
        .exists()
    )


@step("the user is already a group member")
def step_impl(context):
    context.new_group.members.add(context.member_user)


@step("the user is not a group member")
def step_impl(context):
    assert not (
        Privilege.objects.get(id=context.new_group.id)
        .members.all()
        .filter(id=context.member_user.id)
        .exists()
    )


@step("the group id is invalid")
def is_group_member(context):
    context.new_group.id = context.fake.uuid4()
    context.new_group_id = context.new_group.id


@step("the user id is invalid")
def step_impl(context):
    context.member_user.id = context.fake.uuid4()
    context.request = {"user": context.member_user.id}


@step("the member added event is logged")
def step_impl(context):
    context.publisher_mock.notify.assert_called_with(
        str(context.new_group_id), USER_ADDED_TO_GROUP, context.user.id
    )
