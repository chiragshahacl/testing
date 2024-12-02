from cache import remove_cache
from fastapi import APIRouter, Depends, HTTPException
from starlette import status
from starlette.responses import Response

from app.common import schemas as common_schemas
from app.device.src.device import schemas as device_schemas
from app.device.src.device.services import DeviceService

api = APIRouter()


@api.post(
    "/CreateDevice",
    responses={
        status.HTTP_200_OK: {"model": device_schemas.DeviceSchema},
        status.HTTP_401_UNAUTHORIZED: {"model": {}},
        status.HTTP_403_FORBIDDEN: {"model": {}},
        status.HTTP_422_UNPROCESSABLE_ENTITY: {"model": common_schemas.ErrorsSchema},
    },
    operation_id="create-device",
)
@remove_cache("Device")
async def create_device(
    payload: device_schemas.CreateDeviceSchema,
    device_service: DeviceService = Depends(),
) -> device_schemas.DeviceSchema:
    return await device_service.create_device(payload)


@api.post(
    "/UpdateDevice",
    responses={
        status.HTTP_200_OK: {"model": device_schemas.DeviceSchema},
        status.HTTP_401_UNAUTHORIZED: {"model": {}},
        status.HTTP_403_FORBIDDEN: {"model": {}},
        status.HTTP_404_NOT_FOUND: {},
        status.HTTP_422_UNPROCESSABLE_ENTITY: {"model": common_schemas.ErrorsSchema},
    },
    operation_id="update-device",
)
@remove_cache("Device")
async def update_device(
    payload: device_schemas.UpdateDeviceSchema,
    device_service: DeviceService = Depends(),
) -> device_schemas.DeviceSchema:
    if device := await device_service.update_device(payload):
        return device
    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)


@api.post(
    "/BatchAssignLocation",
    responses={
        status.HTTP_204_NO_CONTENT: {"model": {}},
        status.HTTP_401_UNAUTHORIZED: {"model": {}},
        status.HTTP_403_FORBIDDEN: {"model": {}},
        status.HTTP_422_UNPROCESSABLE_ENTITY: {"model": common_schemas.ErrorsSchema},
    },
    operation_id="batch-assign-locations",
)
@remove_cache("Device")
@remove_cache("Bed")
async def batch_assign_location(
    payload: device_schemas.BatchAssignLocationsSchema,
    device_service: DeviceService = Depends(),
) -> Response:
    for association in payload.associations:
        await device_service.assign_location(association.bed_id, association.device_id)

    return Response(status_code=status.HTTP_204_NO_CONTENT)


@api.post(
    "/BatchUnassignLocation",
    responses={
        status.HTTP_204_NO_CONTENT: {"model": {}},
        status.HTTP_401_UNAUTHORIZED: {"model": {}},
        status.HTTP_403_FORBIDDEN: {"model": {}},
        status.HTTP_422_UNPROCESSABLE_ENTITY: {"model": common_schemas.ErrorsSchema},
    },
    operation_id="batch-unassign-locations",
)
@remove_cache("Device")
@remove_cache("Bed")
async def batch_unassign_location(
    payload: device_schemas.BatchUnassignLocationsSchema,
    device_service: DeviceService = Depends(),
) -> Response:
    for device_id in payload.device_ids:
        await device_service.unassign_location(device_id)
    return Response(status_code=status.HTTP_204_NO_CONTENT)


@api.post(
    "/DeleteDevice",
    responses={
        status.HTTP_204_NO_CONTENT: {"model": {}},
        status.HTTP_401_UNAUTHORIZED: {"model": {}},
        status.HTTP_403_FORBIDDEN: {"model": {}},
        status.HTTP_422_UNPROCESSABLE_ENTITY: {"model": common_schemas.ErrorsSchema},
    },
    operation_id="delete-device",
)
@remove_cache("Device")
@remove_cache("Bed")
async def delete_device(
    payload: device_schemas.DeleteDeviceSchema,
    device_service: DeviceService = Depends(),
) -> Response:
    await device_service.delete_device(payload)
    return Response(status_code=status.HTTP_204_NO_CONTENT)
