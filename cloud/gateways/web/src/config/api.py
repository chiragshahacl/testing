from fastapi import APIRouter, Depends
from starlette import status
from starlette.responses import Response

from src.auth.dependencies import TechnicalPasswordRequired
from src.auth.schemas import TechnicalLoginCredential
from src.common.platform.auth import client as auth_client
from src.common.responses import FastJSONResponse
from src.common.schemas import base as common_schemas
from src.config import schemas as config_schemas
from src.config import services as config_services

api = APIRouter(default_response_class=FastJSONResponse)


@api.get(
    "/config",
    responses={
        status.HTTP_200_OK: {"model": config_schemas.WebConfigResources},
        status.HTTP_401_UNAUTHORIZED: {"model": {}},
        status.HTTP_403_FORBIDDEN: {"model": {}},
    },
    operation_id="get-config-list",
    response_class=FastJSONResponse,
)
async def get_config_list(
    config_service: config_services.ConfigService = Depends(),
) -> FastJSONResponse:
    configs = await config_service.get_configs()
    return FastJSONResponse(configs)


@api.put(
    "/config",
    responses={
        status.HTTP_204_NO_CONTENT: {"model": {}},
        status.HTTP_401_UNAUTHORIZED: {"model": {}},
        status.HTTP_403_FORBIDDEN: {"model": {}},
        status.HTTP_422_UNPROCESSABLE_ENTITY: {"model": common_schemas.ErrorSchema},
    },
    operation_id="batch-create-or-update-configs",
    dependencies=[Depends(TechnicalPasswordRequired())],
)
async def batch_create_or_update_configs(
    payload: config_schemas.WebUpdateOrCreateConfigPayload,
    conf_service: config_services.ConfigService = Depends(),
) -> Response:
    credentials = TechnicalLoginCredential.model_construct(password=payload.password)
    token = await auth_client.get_internal_token(credentials)
    if token:
        await conf_service.create_or_update_configs(payload.config)
        return Response(status_code=status.HTTP_204_NO_CONTENT)
