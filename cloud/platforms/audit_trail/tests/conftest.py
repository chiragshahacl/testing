import pytest
import respx
from fastapi.testclient import TestClient

from src.main import app


@pytest.fixture
@respx.mock
def test_app():
    """Test app with mocked HTTPX requests"""
    return TestClient(app, raise_server_exceptions=False)
