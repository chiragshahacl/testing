import secrets
from datetime import UTC, datetime, timedelta
from typing import Optional

import argon2
import jwt
from loguru import logger
from pydantic import BaseModel, Field

from app.auth.enums import RoleNames
from app.auth.models import User
from app.settings import config

ph = argon2.PasswordHasher()


class JWTClaims(BaseModel):
    # default fields
    sub: str
    nbf: float
    exp: float
    jti: str = Field(default_factory=lambda: secrets.token_urlsafe(8))
    aud: str = Field(default_factory=lambda: config.JWT_AUDIENCE)
    iss: str = Field(default_factory=lambda: config.JWT_ISSUER)

    # custom fields
    username: str
    roles: list[RoleNames]


def hash_password(password: str) -> str:
    return ph.hash(password)


def verify_password(password: str, hashed_password: str) -> tuple[bool, bool]:
    try:
        ph.verify(hashed_password, password)
        match = True
    except argon2.exceptions.VerifyMismatchError:
        match = False
    return match, ph.check_needs_rehash(hashed_password)


def get_access_token(user: User) -> str:
    iat = datetime.now(UTC)
    claims = JWTClaims(
        sub=str(user.id),
        nbf=iat.timestamp(),
        exp=(iat + timedelta(minutes=config.JWT_DURATION_MINUTES)).timestamp(),
        roles=[RoleNames(role.name) for role in user.roles],
        username=user.username,
    ).model_dump()
    encoded_jwt = jwt.encode(
        payload=claims, key=config.JWT_SIGNING_KEY, algorithm=config.JWT_ALGORITHM
    )
    return encoded_jwt


def decode_token(token: str) -> Optional[JWTClaims]:
    try:
        claims = jwt.decode(
            token,
            config.JWT_VERIFYING_KEY,
            audience=config.JWT_AUDIENCE,
            algorithms=[config.JWT_ALGORITHM],
        )
    except (
        KeyError,
        jwt.ExpiredSignatureError,
        jwt.InvalidSignatureError,
        jwt.InvalidTokenError,
    ) as e:
        logger.debug(f"Invalid token: {e}")
        return None
    return JWTClaims(**claims)
