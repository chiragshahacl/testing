from uuid import UUID

from fastapi import APIRouter, Depends, Query
from starlette import status
from starlette.responses import Response

from src.cache import add_monitor_not_available_alerts
from src.common.responses import FastJSONResponse
from src.common.schemas import base as common_schemas
from src.device import schemas as web_device_schemas
from src.device import services as device_services

api = APIRouter()


# pylint: disable=too-many-arguments
@api.get(
    "/device",
    responses={
        status.HTTP_200_OK: {"model": web_device_schemas.WebDeviceResources},
        status.HTTP_401_UNAUTHORIZED: {"model": {}},
        status.HTTP_403_FORBIDDEN: {"model": {}},
        status.HTTP_422_UNPROCESSABLE_ENTITY: {"model": common_schemas.ErrorSchema},
    },
    operation_id="get-device-list",
    response_class=FastJSONResponse,
)
async def get_device_list(
    bed_id: list[UUID] = Query(default=None, alias="bedId"),
    gateway_id: UUID = Query(default=None, alias="gatewayId"),
    is_gateway: bool = Query(default=None, alias="isGateway"),
    device_code: str = Query(default=None, alias="deviceCode"),
    bed_group: UUID = Query(default=None, alias="bedGroup"),
    device_service: device_services.DeviceService = Depends(),
) -> FastJSONResponse:
    params = web_device_schemas.WebDeviceQueryParams(
        bed_ids=bed_id,
        gateway_id=gateway_id,
        is_gateway=is_gateway,
        device_code=device_code,
        bed_group=bed_group,
    )
    devices = add_monitor_not_available_alerts(await device_service.get_devices(params))

    return FastJSONResponse(devices)


@api.put(
    "/device/bed/batch",
    responses={
        status.HTTP_204_NO_CONTENT: {"model": {}},
        status.HTTP_401_UNAUTHORIZED: {"model": {}},
        status.HTTP_403_FORBIDDEN: {"model": {}},
        status.HTTP_422_UNPROCESSABLE_ENTITY: {"model": common_schemas.ErrorSchema},
    },
    operation_id="batch-assign-device-bed",
)
async def batch_assign_beds(
    payload: web_device_schemas.WebBatchAssignBedsSchema,
    device_service: device_services.DeviceService = Depends(),
) -> Response:
    await device_service.batch_assign_beds(payload)
    return Response(status_code=status.HTTP_204_NO_CONTENT)


@api.put(
    "/device",
    responses={
        status.HTTP_204_NO_CONTENT: {"model": {}},
        status.HTTP_401_UNAUTHORIZED: {"model": {}},
        status.HTTP_403_FORBIDDEN: {"model": {}},
        status.HTTP_422_UNPROCESSABLE_ENTITY: {"model": common_schemas.ErrorSchema},
    },
    operation_id="create-or-update-device",
)
async def create_or_update_device(
    payload: web_device_schemas.WebCreateOrUpdateDevice,
    device_service: device_services.DeviceService = Depends(),
) -> Response:
    await device_service.create_or_update_device(payload)
    return Response(status_code=status.HTTP_204_NO_CONTENT)


@api.get(
    "/device/{device_id:uuid}/range",
    responses={
        status.HTTP_200_OK: {"model": web_device_schemas.WebDeviceRangesResources},
        status.HTTP_401_UNAUTHORIZED: {"model": {}},
        status.HTTP_403_FORBIDDEN: {"model": {}},
        status.HTTP_422_UNPROCESSABLE_ENTITY: {"model": common_schemas.ErrorSchema},
    },
    operation_id="get-device-vital-ranges",
    response_class=FastJSONResponse,
)
async def get_device_vital_ranges(
    device_id: UUID, device_service: device_services.DeviceService = Depends()
) -> FastJSONResponse:
    ranges = await device_service.get_device_vital_ranges(device_id)
    return FastJSONResponse(ranges)
