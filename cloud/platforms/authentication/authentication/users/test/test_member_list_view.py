# pylint: skip-file
from unittest.mock import MagicMock, patch

import pytest
from django.test import RequestFactory
from django.urls import reverse
from faker import Faker
from features.factories.privilege_factories import PrivilegeFactory
from features.factories.user_factories import AdminUserFactory, RegularUserFactory
from rest_framework.test import APIClient

from authentication.users.views import MembersViewSet


@pytest.mark.django_db
class TestCaseListUsers:
    fake: Faker
    client: APIClient
    user_detail_url: str

    @classmethod
    def setup_class(cls):
        cls.fake = Faker()
        cls.user_detail_url = reverse("user-list")

    def setup_method(self):
        self.client = APIClient()
        self.admin = AdminUserFactory()
        self.client.force_login(self.admin)

    def test_list_user_view_without_pagination(self):
        user_batch_size = 15
        group_users = RegularUserFactory.create_batch(user_batch_size)
        new_group = PrivilegeFactory(users=group_users)

        # create a request object
        request_factory = RequestFactory()
        request = request_factory.get("/")
        request.user = self.admin
        # create a view instance
        view = MembersViewSet.as_view({"get": "list"})
        view.paginate_queryset = MagicMock(return_value=None)

        with patch(
            "authentication.users.views.MembersViewSet.paginate_queryset",
            return_value=None,
        ):
            response = view(request, group_pk=new_group.id)
            assert len(list(response.data)) == user_batch_size
