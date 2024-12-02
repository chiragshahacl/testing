import pytest
from features.factories.app_setting_factories import AppSettingFactory


@pytest.mark.django_db
def test_app_setting_str_method():
    app_setting = AppSettingFactory(key="test_key", value="test_value")

    assert str(app_setting) == "test_key: test_value"
