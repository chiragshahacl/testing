from typing import Annotated

from fastapi import Query, WebSocketException, status
from jwt import decode
from jwt.exceptions import ExpiredSignatureError, InvalidSignatureError
from loguru import logger

from src.settings import config

TOKEN_DESCRIPTION = "Authorization JWT token to decode."


def handle_token_errors(token: str):
    public_key = config.JWT_VERIFYING_KEY
    try:
        decode(token, public_key, algorithms=["RS256"], audience="tucana")
    except (InvalidSignatureError, ExpiredSignatureError) as exc:
        logger.info(f"Authentication error {exc}")
        raise WebSocketException(
            code=status.WS_1008_POLICY_VIOLATION, reason="Authentication error"
        ) from exc
    return token


def get_token(token: Annotated[str, Query(..., description=TOKEN_DESCRIPTION)]) -> str:
    """Decode a JWT token from a query parameter and return the decoded token.

    Args:
        token: The raw JWT token string to decode.

    Returns:
        str: The decoded JWT token.

    Raises:
        WebSocketException 1008: If the token is missing, invalid, or has expired.
    """
    return handle_token_errors(token)
