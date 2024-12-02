import pytest
from django.urls import reverse
from rest_framework.test import APIClient


@pytest.mark.django_db
def test_health_endpoint():
    client = APIClient()
    check_health_url = reverse("health_check:health_check_home")
    response = client.get(
        check_health_url,
        {"format": "json"},
        content_type="application/json",
        format="json",
        headers={"Accept": "application/json"},
    )
    assert response.status_code == 200
