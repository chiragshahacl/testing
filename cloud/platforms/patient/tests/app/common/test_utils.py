from app.common.utils import ScopeConfiguration


def test_scope_config_init(mocker):
    mocker.MagicMock(spec=ScopeConfiguration)
    init_mock = mocker.patch.object(ScopeConfiguration, "__init__", return_value=None)
    ScopeConfiguration({}, {})
    init_mock.assert_called_once_with({}, {})


def test_scope_config_call(mocker):
    mocker.MagicMock(spec=ScopeConfiguration)
    call_mock = mocker.patch.object(ScopeConfiguration, "__call__", return_value=None)
    scope_config = ScopeConfiguration({}, {})
    scope_config()
    call_mock.assert_called_once_with()
