import uuid

from pydantic import AfterValidator, ConfigDict, SecretStr
from typing_extensions import Annotated

from app.common.exceptions import BaseValidationException
from app.common.schemas import BaseSchema, ErrorSchema
from app.settings import config


class InvalidPasswordLength(BaseValidationException):
    def __init__(self) -> None:
        self.error = ErrorSchema(
            loc=["body", "password"],
            msg="Invalid password length",
            type="value_error.invalid_password_length",
        )


class PasswordShouldContainANumber(BaseValidationException):
    def __init__(self) -> None:
        self.error = ErrorSchema(
            loc=["body", "password"],
            msg="Password must contain number",
            type="value_error.password_must_contain_a_number",
        )


class PasswordShouldContainALowercaseLetter(BaseValidationException):
    def __init__(self) -> None:
        self.error = ErrorSchema(
            loc=["body", "password"],
            msg="Password must contain a lowercase letter",
            type="value_error.password_must_contain_a_lowercase_letter",
        )


class PasswordShouldContainAnUppercaseLetter(BaseValidationException):
    def __init__(self) -> None:
        self.error = ErrorSchema(
            loc=["body", "password"],
            msg="Password must contain an uppercase letter",
            type="value_error.password_must_contain_an_uppercase_letter",
        )


class PasswordShouldContainASpecialCharacter(BaseValidationException):
    def __init__(self) -> None:
        self.error = ErrorSchema(
            loc=["body", "password"],
            msg="Password must contain an uppercase character",
            type="value_error.password_must_contain_a_special_character",
        )


def check_password_requirements(v: str) -> bool:
    special_chars = {
        "$",
        "@",
        "#",
        "%",
        "!",
        "^",
        "&",
        "*",
        "(",
        ")",
        "-",
        "_",
        "+",
        "=",
        "{",
        "}",
        "[",
        "]",
    }
    if len(v) < config.USER_PASSWORD_MINIMUM_LENGTH:
        raise InvalidPasswordLength()
    if config.USER_PASSWORD_REQUIRE_NUMBERS and not any(char.isdigit() for char in v):
        raise PasswordShouldContainANumber()
    if config.USER_PASSWORD_REQUIRE_UPPERCASE and not any(char.isupper() for char in v):
        raise PasswordShouldContainAnUppercaseLetter()
    if config.USER_PASSWORD_REQUIRE_LOWERCASE and not any(char.islower() for char in v):
        raise PasswordShouldContainALowercaseLetter()
    if config.USER_PASSWORD_REQUIRE_SPECIAL_CHARS and not any(char in special_chars for char in v):
        raise PasswordShouldContainASpecialCharacter()
    return v


SecretPassword = Annotated[SecretStr, AfterValidator(check_password_requirements)]


class RoleSchema(BaseSchema):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID


class CreateUserSchema(BaseSchema):
    username: str
    password: SecretPassword
    roles: list[RoleSchema]


class UserSchema(BaseSchema):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    username: str
    roles: list[RoleSchema]
