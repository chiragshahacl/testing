import pytest
from django.conf import settings
from features.factories.privilege_factories import PrivilegeFactory
from features.factories.user_factories import AdminUserFactory, RegularUserFactory

from authentication.users.models import Privilege


@pytest.mark.django_db
def test_user_str_method():
    user = RegularUserFactory(username="test_user")

    # check that the string representation of the user is the username
    assert str(user) == "test_user"


@pytest.mark.django_db
def test_add_admin_users_to_admin_group_automatically():
    admin_user = AdminUserFactory()
    admin_group = Privilege.objects.get(name=settings.ADMIN_PRIVILEGE_NAME)

    assert admin_group.members.filter(id=admin_user.id).exists()


@pytest.mark.django_db
def test_privilege_str_method():
    user = PrivilegeFactory(name="test_privilege")

    # check that the string representation of the privilege is the name
    assert str(user) == "test_privilege"
