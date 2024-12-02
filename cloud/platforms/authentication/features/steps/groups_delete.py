from authentication.users.models import Privilege
from authentication.users.signals import GROUP_REMOVED
from behave import *
from django.urls import reverse

from features.factories.privilege_factories import PrivilegeFactory
from features.factories.user_factories import RegularUserFactory


@step("a user group exists")
def step_impl(context):
    context.user_batch_size = 15
    context.group_users = RegularUserFactory.create_batch(context.user_batch_size)
    context.new_group = PrivilegeFactory(users=context.group_users)
    context.new_group_id = context.new_group.id


@when("request to delete the user group")
def step_impl(context):
    group_detail_url = reverse("group-detail", kwargs={"pk": context.new_group_id})
    access_token = context.user_session.access
    context.response = context.test.client.delete(
        group_detail_url, headers={"Authorization": f"Bearer {access_token}"}
    )


@step("the group is deleted")
def step_impl(context):
    assert not (Privilege.objects.filter(pk=context.new_group_id).exists())
    for user in context.group_users:
        assert not (user.privileges.filter(pk=context.new_group_id).exists())


@step("the user group to delete does not exit")
def step_impl(context):
    context.new_group_id = context.fake.uuid4()


@step("the group deleted event is logged")
def step_impl(context):
    context.publisher_mock.notify.assert_called_with(
        str(context.new_group_id), GROUP_REMOVED, context.user.id
    )
