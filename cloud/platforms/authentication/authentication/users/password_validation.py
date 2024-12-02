from django.core.exceptions import ValidationError
from django.utils.translation import gettext as _


class LowerCaseValidator:
    def validate(self, password, user=None):  # pylint: disable=W0613
        if not any(char.islower() for char in password):
            raise ValidationError(
                _("This password must contain at least one lowercase letter."),
                code="password_missing_lowercase_letter",
            )

    def get_help_text(self):
        return _("Your password must contain at least one lowercase letter.")


class UpperCaseValidator:
    def validate(self, password, user=None):  # pylint: disable=W0613
        if not any(char.isupper() for char in password):
            raise ValidationError(
                _("This password must contain at least one uppercase letter."),
                code="password_missing_uppercase_letter",
            )

    def get_help_text(self):
        return _("Your password must contain at least one uppercase letter.")


class NumberValidator:
    def validate(self, password, user=None):  # pylint: disable=W0613
        if not any(char.isdigit() for char in password):
            raise ValidationError(
                _("This password must contain at least one number."),
                code="password_missing_number_character",
            )

    def get_help_text(self):
        return _("Your password must contain at least one number.")


class SpecialCharacterValidator:
    def __init__(self, special_characters=r"!\"#$%&'()*+,-./:;<=>?@[\]^_`{|}~"):
        self.special_characters = special_characters

    def validate(self, password, user=None):  # pylint: disable=W0613
        if not any(char in self.special_characters for char in password):
            raise ValidationError(
                _("This password must contain at least one special character."),
                code="password_missing_number_character",
                params={"special_characters": self.special_characters},
            )

    def get_help_text(self):
        return _("Your password must contain at least one special character.")
