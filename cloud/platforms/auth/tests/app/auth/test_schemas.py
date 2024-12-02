from unittest.mock import patch

import pytest

from app.auth.schemas import (
    InvalidPasswordLength,
    PasswordShouldContainALowercaseLetter,
    PasswordShouldContainANumber,
    PasswordShouldContainAnUppercaseLetter,
    PasswordShouldContainASpecialCharacter,
    check_password_requirements,
)
from app.common.schemas import ErrorSchema
from app.settings import config


@pytest.fixture
def mock_config():
    """Fixture to mock configuration settings."""
    with patch.object(config, "USER_PASSWORD_MINIMUM_LENGTH", 8), patch.object(
        config, "USER_PASSWORD_REQUIRE_NUMBERS", False
    ), patch.object(config, "USER_PASSWORD_REQUIRE_LOWERCASE", False), patch.object(
        config, "USER_PASSWORD_REQUIRE_UPPERCASE", False
    ), patch.object(config, "USER_PASSWORD_REQUIRE_SPECIAL_CHARS", False):
        yield


def test_valid_password(mock_config):
    """Test that a valid password passes validation."""
    assert check_password_requirements("Valid123!") == "Valid123!"


def test_invalid_length(mock_config):
    """Test that a password failing length validation raises the correct exception."""
    with patch.object(config, "USER_PASSWORD_MINIMUM_LENGTH", 10):
        with pytest.raises(InvalidPasswordLength) as exc:
            check_password_requirements("Short1!")
        assert exc.value.error == ErrorSchema(
            loc=["body", "password"],
            msg="Invalid password length",
            type="value_error.invalid_password_length",
        )


def test_missing_number(mock_config):
    """Test that a password missing a number raises the correct exception."""
    with patch.object(config, "USER_PASSWORD_REQUIRE_NUMBERS", True):
        with pytest.raises(PasswordShouldContainANumber) as exc:
            check_password_requirements("NoNumbers!")
        assert exc.value.error == ErrorSchema(
            loc=["body", "password"],
            msg="Password must contain number",
            type="value_error.password_must_contain_a_number",
        )


def test_missing_lowercase(mock_config):
    """Test that a password missing a lowercase letter raises the correct exception."""
    with patch.object(config, "USER_PASSWORD_REQUIRE_LOWERCASE", True):
        with pytest.raises(PasswordShouldContainALowercaseLetter) as exc:
            check_password_requirements("UPPERCASE123!")
        assert exc.value.error == ErrorSchema(
            loc=["body", "password"],
            msg="Password must contain a lowercase letter",
            type="value_error.password_must_contain_a_lowercase_letter",
        )


def test_missing_uppercase(mock_config):
    """Test that a password missing an uppercase letter raises the correct exception."""
    with patch.object(config, "USER_PASSWORD_REQUIRE_UPPERCASE", True):
        with pytest.raises(PasswordShouldContainAnUppercaseLetter) as exc:
            check_password_requirements("lowercase123!")
        assert exc.value.error == ErrorSchema(
            loc=["body", "password"],
            msg="Password must contain an uppercase letter",
            type="value_error.password_must_contain_an_uppercase_letter",
        )


def test_missing_special_character(mock_config):
    """Test that a password missing a special character raises the correct exception."""
    with patch.object(config, "USER_PASSWORD_REQUIRE_SPECIAL_CHARS", True):
        with pytest.raises(PasswordShouldContainASpecialCharacter) as exc:
            check_password_requirements("NoSpecial123")
        assert exc.value.error == ErrorSchema(
            loc=["body", "password"],
            msg="Password must contain an uppercase character",
            type="value_error.password_must_contain_a_special_character",
        )


def test_all_requirements_met(mock_config):
    """Test that a password meeting all requirements passes validation."""
    with patch.object(config, "USER_PASSWORD_REQUIRE_NUMBERS", True), patch.object(
        config, "USER_PASSWORD_REQUIRE_LOWERCASE", True
    ), patch.object(config, "USER_PASSWORD_REQUIRE_UPPERCASE", True), patch.object(
        config, "USER_PASSWORD_REQUIRE_SPECIAL_CHARS", True
    ):
        assert check_password_requirements("Valid123!") == "Valid123!"
