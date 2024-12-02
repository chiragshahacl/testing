from fastapi import Depends, HTTPException
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from jwt import decode
from jwt.exceptions import (
    ExpiredSignatureError,
    InvalidSignatureError,
    InvalidTokenError,
)
from starlette import status
from starlette.requests import Request

from app.auth.crypto import JWTClaims
from app.auth.enums import RoleNames
from app.settings import config


class InternalAuthRequired:
    async def __call__(
        self,
        request: Request,
        auth_credentials: HTTPAuthorizationCredentials = Depends(HTTPBearer()),
    ) -> JWTClaims:
        internal_token = auth_credentials.credentials
        public_key = config.JWT_VERIFYING_KEY
        try:
            claims = decode(
                internal_token,
                public_key,
                audience=config.JWT_AUDIENCE,
                algorithms=[config.JWT_ALGORITHM],
            )
            request.state.internal_token = internal_token
            request.state.internal_claims = claims
            request.state.username = claims["username"]
        except (
            KeyError,
            ExpiredSignatureError,
            InvalidSignatureError,
            InvalidTokenError,
        ) as exc:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED) from exc
        return JWTClaims(**claims)


class UserHasRole:
    def __init__(self, roles: set[RoleNames]):
        self.required_roles = roles

    async def __call__(self, claims: JWTClaims = Depends(InternalAuthRequired())) -> JWTClaims:
        for role in claims.roles:
            if role in self.required_roles:
                return claims
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN)
