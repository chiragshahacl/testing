from unittest.mock import MagicMock, patch

import pytest
from fastapi import WebSocketException, status
from jwt import ExpiredSignatureError, InvalidSignatureError

from src.realtime.authentication import get_token, handle_token_errors
from src.settings import config

logger = MagicMock(info=MagicMock())


@patch("src.realtime.authentication.decode")
def test_handle_token_errors_valid_token(mock_decode):
    token = "valid_token"
    result = handle_token_errors(token)
    assert result == token
    mock_decode.assert_called_once_with(
        token, config.JWT_VERIFYING_KEY, algorithms=["RS256"], audience="tucana"
    )


@patch("src.realtime.authentication.decode")
def test_handle_token_errors_invalid_signature_error(mock_decode):
    mock_decode.side_effect = InvalidSignatureError("Invalid signature")
    with pytest.raises(WebSocketException) as exc_info:
        handle_token_errors("invalid_token")

    assert exc_info.value.code == status.WS_1008_POLICY_VIOLATION
    assert exc_info.value.reason == "Authentication error"


@patch("src.realtime.authentication.decode")
def test_handle_token_errors_expired_signature_error(mock_decode):
    mock_decode.side_effect = ExpiredSignatureError("Token expired")
    with pytest.raises(WebSocketException) as exc_info:
        handle_token_errors("expired_token")

    assert exc_info.value.code == status.WS_1008_POLICY_VIOLATION
    assert exc_info.value.reason == "Authentication error"


@patch("src.realtime.authentication.handle_token_errors")
def test_get_token(mock_handle_token_errors):
    token = "valid_token"
    mock_handle_token_errors.return_value = token

    result = get_token(token)

    assert result == token
    mock_handle_token_errors.assert_called_once_with(token)
