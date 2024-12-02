"""
Context:
This function creates a valid token that can be used by our HL7 gateway to make API calls
to our internal microservices.
Since there is no authentication support on the service, a pre-provided token must be used.

Parameters:
- `username` (str): The username to authenticate with.
- `raw_password` (str): The raw password to authenticate with.

Returns:
None. The function prints the JWT and the decoded values for access
      and refresh tokens to the console.

Usage:
1. Start an interactive command-line by running `python manage.py shell`.
2. Import the function: `from authentication.users.test.create_hl7_token import create_hl7_token`.
3. Call the function with the correct parameters:
   `create_hl7_token(username="the_username", raw_password="the_password")`.
   Replace the `username` and `raw_password` parameters with the correct values.

Note: The generated token is valid for three years.
This function temporarily changes the `ACCESS_TOKEN_LIFETIME`
and `REFRESH_TOKEN_LIFETIME` settings from the `SIMPLE_JWT` configuration
to set the token's lifespan to 3 years.
After generating the token, the function restores the original lifespan
settings to their previous values.

Example Usage:
from authentication.users.test.create_hl7_token import create_hl7_token
create_hl7_token(username="admin@sibelhealth.com", raw_password="hi123")
"""

from datetime import datetime, timedelta

import jwt
from django.conf import settings
from django.urls import reverse
from rest_framework.test import APIClient

from authentication.users.management.commands.create_internal_token import (
    Command as CreateInternalTokenCommand,
)


def create_hl7_token(username, raw_password):
    # Change TTL setting
    current_access_token_lifetime = settings.SIMPLE_JWT.get("ACCESS_TOKEN_LIFETIME")
    current_refresh_token_lifetime = settings.SIMPLE_JWT.get("REFRESH_TOKEN_LIFETIME")
    settings.SIMPLE_JWT["ACCESS_TOKEN_LIFETIME"] = timedelta(days=1095)
    settings.SIMPLE_JWT["REFRESH_TOKEN_LIFETIME"] = timedelta(days=1095)

    client = APIClient()
    token_obtain_url = reverse("token_obtain_pair")

    data = {"username": username, "password": raw_password}
    response = client.post(token_obtain_url, data)

    user_session = response.data
    access_token = user_session.get("access")
    refresh_token = user_session.get("refresh")

    decoded_access = jwt.decode(
        access_token,
        settings.SIMPLE_JWT.get("VERIFYING_KEY"),
        audience=settings.SIMPLE_JWT.get("AUDIENCE"),
        algorithms=[settings.SIMPLE_JWT.get("ALGORITHM")],
    )

    decoded_refresh = jwt.decode(
        refresh_token,
        settings.SIMPLE_JWT.get("VERIFYING_KEY"),
        audience=settings.SIMPLE_JWT.get("AUDIENCE"),
        algorithms=[settings.SIMPLE_JWT.get("ALGORITHM")],
    )

    # Rollback settings
    settings.SIMPLE_JWT["ACCESS_TOKEN_LIFETIME"] = current_access_token_lifetime
    settings.SIMPLE_JWT["REFRESH_TOKEN_LIFETIME"] = current_refresh_token_lifetime

    print("========= JWT TOKEN START =========")
    print(user_session)
    print("========== JWT TOKEN END ==========")
    print(f"Decoded access token => {decoded_access}")
    print(f"Decoded refresh token => {decoded_refresh}")


def test_manage_py_token_creation():
    token = CreateInternalTokenCommand().handle(duration_days=10)
    claims = jwt.decode(
        token,
        settings.SIMPLE_JWT["VERIFYING_KEY"],
        algorithms="RS256",
        audience="tucana",
    )
    assert token
    assert claims
    assert claims["exp"] == int((datetime.now() + timedelta(days=10)).timestamp())
