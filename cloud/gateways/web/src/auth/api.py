from fastapi import APIRouter, Depends
from starlette import status
from starlette.responses import Response

from src.auth import schemas as auth_schemas
from src.auth.dependencies import InternalAuthRequired, PasswordRequired, TechnicalPasswordRequired
from src.auth.schemas import LogoutSchema, WebChangePasswordPayload
from src.auth.services import PlatformAuthenticationService
from src.common.platform.auth import client as auth_client
from src.common.responses import FastJSONResponse

api = APIRouter(default_response_class=FastJSONResponse)


@api.post(
    "/auth/token",
    responses={
        status.HTTP_200_OK: {"model": auth_schemas.InternalToken},
        status.HTTP_401_UNAUTHORIZED: {},
        status.HTTP_403_FORBIDDEN: {},
    },
    operation_id="post-web-auth-api",
    dependencies=[Depends(PasswordRequired())],
    description=(
        "This endpoint authenticates a user by validating "
        "the provided credentials and, upon successful verification, "
        "returns an authentication token. The token can be used to "
        "access other secure endpoints within the application."
        "If username is not provided, it will use the system default."
        "The response will include the token and refresh token"
        "The validity of each token can be found in the `ttl` field contained"
        " in the token payload (please note the token is base64 encoded)."
    )
)
async def get_internal_token_api(
    payload: auth_schemas.LoginCredential,
) -> FastJSONResponse:
    token = await auth_client.get_internal_token(payload)
    return FastJSONResponse(token)


@api.post(
    "/auth/token/refresh",
    responses={
        status.HTTP_200_OK: {"model": auth_schemas.RefreshedInternalToken},
        status.HTTP_401_UNAUTHORIZED: {},
        status.HTTP_403_FORBIDDEN: {},
    },
    operation_id="post-web-auth-refresh-api",
    description=(
        "This endpoint allows a user to refresh their authentication token, "
        "extending access without requiring a full re-authentication. The "
        "client provides a refresh token, which the server verifies and, "
        "if valid, issues a new authentication token."
    )
)
async def refresh_token_api(
    payload: auth_schemas.RefreshToken,
) -> FastJSONResponse:
    token = await auth_client.refresh_internal_token(payload)
    return FastJSONResponse(token)


@api.post(
    "/auth/token/logout",
    responses={
        status.HTTP_204_NO_CONTENT: {},
        status.HTTP_401_UNAUTHORIZED: {},
        status.HTTP_403_FORBIDDEN: {},
    },
    operation_id="post-web-auth-logout-api",
    dependencies=[Depends(InternalAuthRequired())],
    description="This endpoint closes the user session."
)
async def logout_api(
    payload: LogoutSchema,
    platform_auth_service: PlatformAuthenticationService = Depends(),
) -> Response:
    await platform_auth_service.auth_client.logout(payload.to_platform())
    return Response(status_code=status.HTTP_204_NO_CONTENT)


@api.post(
    "/auth/change-password",
    responses={
        status.HTTP_204_NO_CONTENT: {},
        status.HTTP_401_UNAUTHORIZED: {},
        status.HTTP_403_FORBIDDEN: {},
    },
    operation_id="post-web-auth-change-password-api",
    dependencies=[Depends(InternalAuthRequired())],
    description=(
        "This endpoint allows an authenticated user to change their password. "
        "The user must provide the necessary information in the payload to verify "
        "their current password and specify a new password."
    )
)
async def change_password(
    payload: WebChangePasswordPayload,
    platform_auth_service: PlatformAuthenticationService = Depends(),
) -> Response:
    await platform_auth_service.change_password(payload)
    return Response(status_code=status.HTTP_204_NO_CONTENT)


@api.post(
    "/auth/technical/token",
    responses={
        status.HTTP_200_OK: {"model": auth_schemas.InternalToken},
        status.HTTP_401_UNAUTHORIZED: {},
        status.HTTP_403_FORBIDDEN: {},
    },
    operation_id="post-web-auth-technical-api",
    dependencies=[Depends(TechnicalPasswordRequired())],
    description=(
        "This endpoint generates an authentication token specifically "
        "for technical users or services, allowing them to interact with "
        "internal APIs securely. If username is not provided, it will use the system default."
    )
)
async def get_technical_internal_token_api(
    payload: auth_schemas.TechnicalLoginCredential,
) -> FastJSONResponse:
    token = await auth_client.get_internal_token(payload)
    return FastJSONResponse(token)
