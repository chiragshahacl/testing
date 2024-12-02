from uuid import UUID

from cache import add_cache
from fastapi import APIRouter, Depends
from starlette import status
from starlette.requests import Request

from app.bed.schemas import BedGroupResourcesSchema, BedResourcesSchema
from app.bed.services import BedService

api = APIRouter()


@api.get(
    "/bed",
    responses={
        status.HTTP_200_OK: {"model": BedResourcesSchema},
        status.HTTP_401_UNAUTHORIZED: {"model": {}},
        status.HTTP_403_FORBIDDEN: {"model": {}},
    },
)
@add_cache("Bed")
async def get_beds(
    request: Request,  # pylint: disable=unused-argument
    service: BedService = Depends(),
) -> BedResourcesSchema:
    beds = await service.get_beds()
    return beds


@api.get(
    "/bed-group",
    responses={
        status.HTTP_200_OK: {"model": BedGroupResourcesSchema},
        status.HTTP_401_UNAUTHORIZED: {"model": {}},
        status.HTTP_403_FORBIDDEN: {"model": {}},
    },
    operation_id="get-bed-groups",
)
@add_cache("BedGroup")
async def get_bed_groups(
    request: Request,  # pylint: disable=unused-argument
    service: BedService = Depends(),
) -> BedGroupResourcesSchema:
    groups = await service.get_bed_groups()
    return groups


@api.get(
    "/bed-group/{group_id:uuid}/beds",
    responses={
        status.HTTP_200_OK: {"model": BedResourcesSchema},
        status.HTTP_401_UNAUTHORIZED: {"model": {}},
        status.HTTP_403_FORBIDDEN: {"model": {}},
    },
    operation_id="get-beds-for-group",
)
@add_cache("Bed")
async def get_beds_in_group(
    request: Request,  # pylint: disable=unused-argument
    group_id: UUID,
    service: BedService = Depends(),
) -> BedResourcesSchema:
    resources = await service.get_group_beds(group_id)
    return resources
