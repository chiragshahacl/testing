from typing import Any, Dict

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

from src.settings import settings


class InternalAuthRequired:
    async def __call__(
        self,
        request: Request,
        auth_credentials: HTTPAuthorizationCredentials = Depends(HTTPBearer()),
    ) -> Dict[str, Any]:
        internal_token = auth_credentials.credentials
        public_key = settings.JWT_VERIFYING_KEY
        try:
            claims = decode(internal_token, public_key, audience="tucana", algorithms=["RS256"])
            request.state.internal_token = internal_token
            request.state.internal_claims = claims
            request.state.username = claims["user_id"]
        except (
            KeyError,
            ExpiredSignatureError,
            InvalidSignatureError,
            InvalidTokenError,
        ) as exc:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED) from exc
        return claims


class PasswordRequired:
    async def __call__(
        self,
        request: Request,
    ) -> Dict[str, Any]:
        body = await request.json()
        request.state.username = settings.DEFAULT_ADMIN_USERNAME
        return body


class TechnicalPasswordRequired:
    async def __call__(
        self,
        request: Request,
    ) -> Dict[str, Any]:
        body = await request.json()
        request.state.username = settings.DEFAULT_TECHNICAL_USER_USERNAME
        return body
