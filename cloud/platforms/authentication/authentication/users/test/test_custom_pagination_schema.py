from collections import OrderedDict
from unittest.mock import Mock, patch

from django.core.paginator import Paginator

from authentication.users.pagination import PageNumberResourcesPagination


class TestPageNumberResourcesPagination:
    def test_get_paginated_response(self):
        data = ["resource1", "resource2", "resource3"]
        pagination = Paginator(data, 10)
        page = pagination.page(1)
        paginator = PageNumberResourcesPagination()
        paginator.page = page

        with patch.dict(paginator.page.paginator.__dict__, {"count": 3}), patch.object(
            paginator, "get_next_link", return_value=None
        ), patch.object(paginator, "get_previous_link", return_value=None):
            response = paginator.get_paginated_response(data)

        expected_response_data = OrderedDict(
            [
                ("count", 3),
                ("next", None),
                ("previous", None),
                ("resources", data),
            ]
        )
        assert response.data == expected_response_data

    def test_get_paginated_response_schema(self):
        pagination = PageNumberResourcesPagination()
        mock_schema = Mock()

        response_schema = pagination.get_paginated_response_schema(mock_schema)
        assert response_schema
