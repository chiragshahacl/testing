from authentication.users.password_validation import (
    LowerCaseValidator,
    NumberValidator,
    SpecialCharacterValidator,
    UpperCaseValidator,
)


def test_lower_case_validator_help_text():
    lower_case_validator = LowerCaseValidator()
    expected_help_text = "Your password must contain at least one lowercase letter."
    assert lower_case_validator.get_help_text() == expected_help_text


def test_upper_case_validator_help_text():
    upper_case_validator = UpperCaseValidator()
    expected_help_text = "Your password must contain at least one uppercase letter."
    assert upper_case_validator.get_help_text() == expected_help_text


def test_number_validator_help_text():
    number_validator = NumberValidator()
    expected_help_text = "Your password must contain at least one number."
    assert number_validator.get_help_text() == expected_help_text


def test_special_character_validator_help_text():
    special_character_validator = SpecialCharacterValidator()
    expected_help_text = "Your password must contain at least one special character."
    assert special_character_validator.get_help_text() == expected_help_text
