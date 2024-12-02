from uuid import UUID

from cache import add_cache
from fastapi import APIRouter, Depends, HTTPException
from starlette import status
from starlette.requests import Request

from app.device.src.device import schemas as device_schemas
from app.device.src.device.services import DeviceService
from app.encounter import schemas as encounter_schemas

api = APIRouter()


@api.get(
    "/{device_id}",
    responses={
        status.HTTP_200_OK: {"model": device_schemas.DeviceResource},
        status.HTTP_401_UNAUTHORIZED: {"model": {}},
        status.HTTP_403_FORBIDDEN: {"model": {}},
        status.HTTP_404_NOT_FOUND: {"model": {}},
    },
    operation_id="get-device-by-identifier",
)
@add_cache("Device")
async def get_device_by_identifier(
    request: Request,  # pylint: disable= W0613
    device_id: str,
    device_service: DeviceService = Depends(),
) -> device_schemas.DeviceResource:
    if not (device := await device_service.get_device_by_identifier(device_id)):
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)
    return device


@api.get(
    "",
    responses={
        status.HTTP_200_OK: {"model": device_schemas.DeviceResources},
        status.HTTP_401_UNAUTHORIZED: {"model": {}},
        status.HTTP_403_FORBIDDEN: {"model": {}},
        status.HTTP_404_NOT_FOUND: {"model": {}},
    },
    operation_id="get-device-list",
)
@add_cache("Device")
async def get_all_devices(
    request: Request,  # pylint: disable=W0613
    params: device_schemas.DeviceQueryParams = Depends(),
    device_service: DeviceService = Depends(),
) -> device_schemas.DeviceResources:
    devices = await device_service.get_all_devices(params)
    return devices


@api.get(
    "/{device_id}/ranges",
    responses={
        status.HTTP_200_OK: {"model": device_schemas.VitalRangesResources},
        status.HTTP_401_UNAUTHORIZED: {"model": {}},
        status.HTTP_403_FORBIDDEN: {"model": {}},
        status.HTTP_404_NOT_FOUND: {"model": {}},
    },
    operation_id="get-device-vital-ranges",
)
@add_cache("Device")
async def get_device_vital_ranges(
    request: Request,  # pylint: disable=W0613
    device_id: UUID,
    device_service: DeviceService = Depends(),
) -> device_schemas.VitalRangesResources:
    ranges = await device_service.get_device_vital_ranges(device_id)
    return ranges


@api.get(
    "/{primary_identifier}/admission",
    responses={
        status.HTTP_200_OK: {"model": encounter_schemas.AdmissionResource},
        status.HTTP_401_UNAUTHORIZED: {"model": {}},
        status.HTTP_403_FORBIDDEN: {"model": {}},
        status.HTTP_404_NOT_FOUND: {"model": {}},
    },
    operation_id="get-device-encounters",
)
async def get_device_admissions(
    request: Request,  # pylint: disable=W0613
    primary_identifier: str,
    device_service: DeviceService = Depends(),
) -> encounter_schemas.AdmissionResource:
    admission = await device_service.get_device_encounters(primary_identifier)
    return admission
