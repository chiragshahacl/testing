from src.health_check.api import api as health_check_api
from src.main import create_app
from src.settings import settings


def test_endpoints_starts_with_base_path(test_app):
    for route in test_app.app.routes:
        if not route.path.startswith("/health"):
            assert route.path.startswith(settings.BASE_PATH)


def test_health_api_is_added_with_no_base_path(mocker):
    app_mock = mocker.patch("src.main.FastAPI").return_value

    result = create_app()

    assert result is app_mock
    assert mocker.call(health_check_api, tags=["HealthCheck"]) in app_mock.include_router.mock_calls
