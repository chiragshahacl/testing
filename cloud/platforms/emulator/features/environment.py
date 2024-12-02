from pathlib import Path

import respx
from behave import fixture, use_fixture
from behave.runner import Context
from fastapi.testclient import TestClient

from src.main import app

BASE_DIR = Path(__file__).parent.parent


@fixture
def create_test_client(context: Context):
    """Test app with mocked HTTPX requests"""
    with respx.mock:
        context.client = TestClient(app, raise_server_exceptions=False)
        yield context.client
        context.client.close()


def before_scenario(context: Context, _):
    use_fixture(create_test_client, context)
