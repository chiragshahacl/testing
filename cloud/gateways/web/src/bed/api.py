from fastapi import APIRouter, Depends
from starlette import status
from starlette.responses import Response

from src.bed import schemas as web_bed_schemas
from src.bed import services as bed_services
from src.common.responses import FastJSONResponse
from src.common.schemas import base as common_schemas

api = APIRouter()


@api.get(
    "/bed",
    responses={
        status.HTTP_200_OK: {"model": web_bed_schemas.WebBedResources},
        status.HTTP_401_UNAUTHORIZED: {"model": {}},
        status.HTTP_403_FORBIDDEN: {"model": {}},
        status.HTTP_422_UNPROCESSABLE_ENTITY: {"model": common_schemas.ErrorSchema},
    },
    operation_id="get-bed-list",
    response_class=FastJSONResponse,
)
async def get_bed_list(
    bed_service: bed_services.BedService = Depends(),
) -> FastJSONResponse:
    beds = await bed_service.get_beds()
    return FastJSONResponse(beds)


@api.post(
    "/bed/batch",
    responses={
        status.HTTP_200_OK: {"model": web_bed_schemas.WebBedResources},
        status.HTTP_401_UNAUTHORIZED: {"model": {}},
        status.HTTP_403_FORBIDDEN: {"model": {}},
        status.HTTP_422_UNPROCESSABLE_ENTITY: {"model": common_schemas.ErrorSchema},
    },
    operation_id="batch-create-beds",
)
async def batch_create_beds(
    payload: web_bed_schemas.WebBatchCreateBeds,
    bed_service: bed_services.BedService = Depends(),
) -> web_bed_schemas.WebBedResources:
    beds = await bed_service.batch_create_beds(payload)
    return beds


@api.put(
    "/bed/batch",
    responses={
        status.HTTP_204_NO_CONTENT: {"model": {}},
        status.HTTP_401_UNAUTHORIZED: {"model": {}},
        status.HTTP_403_FORBIDDEN: {"model": {}},
        status.HTTP_422_UNPROCESSABLE_ENTITY: {"model": common_schemas.ErrorSchema},
    },
    operation_id="batch-create-or-update-beds",
)
async def batch_create_or_update_beds(
    payload: web_bed_schemas.WebBatchCreateOrUpdateBeds,
    bed_service: bed_services.BedService = Depends(),
) -> Response:
    await bed_service.create_or_update_beds(payload)
    return Response(status_code=status.HTTP_204_NO_CONTENT)


@api.delete(
    "/bed/batch",
    responses={
        status.HTTP_204_NO_CONTENT: {"model": {}},
        status.HTTP_401_UNAUTHORIZED: {"model": {}},
        status.HTTP_403_FORBIDDEN: {"model": {}},
        status.HTTP_422_UNPROCESSABLE_ENTITY: {"model": common_schemas.ErrorSchema},
    },
    operation_id="batch-delete-beds",
)
async def batch_delete_beds(
    payload: web_bed_schemas.WebBatchDeleteBeds,
    bed_service: bed_services.BedService = Depends(),
) -> Response:
    await bed_service.batch_delete_beds(payload)
    return Response(status_code=status.HTTP_204_NO_CONTENT)
