from cache import remove_cache
from fastapi import APIRouter, Depends
from starlette import status
from starlette.responses import Response

from app.bed.schemas import (
    AddBedToGroupSchema,
    BatchAssignBedsSchema,
    BatchCreateBedGroupsSchema,
    BatchCreateBedsSchema,
    BatchDeleteBedGroupsSchema,
    BatchDeleteBedSchema,
    BatchUpdateBedGroupsSchema,
    BatchUpdateBedsSchema,
    BedGroupResourcesSchema,
    BedGroupSchema,
    BedResourcesSchema,
    BedSchema,
    CreateBedGroupSchema,
    CreateBedSchema,
    DeleteBedGroupSchema,
    DeleteBedSchema,
    RemoveBedFromGroupSchema,
)
from app.bed.services import BedService
from app.common.schemas import ErrorsSchema

api = APIRouter()


@api.post(
    "/bed/BatchCreateBeds",
    responses={
        status.HTTP_200_OK: {"model": BedResourcesSchema},
        status.HTTP_401_UNAUTHORIZED: {"model": {}},
        status.HTTP_403_FORBIDDEN: {"model": {}},
        status.HTTP_422_UNPROCESSABLE_ENTITY: {"model": ErrorsSchema},
    },
    operation_id="batch-create-beds",
)
@remove_cache("Bed")
async def batch_create_beds(
    payload: BatchCreateBedsSchema,
    service: BedService = Depends(),
) -> BedResourcesSchema:
    beds = await service.batch_create_beds(payload.beds)
    return beds


@api.post(
    "/bed/CreateBed",
    responses={
        status.HTTP_200_OK: {"model": BedSchema},
        status.HTTP_401_UNAUTHORIZED: {"model": {}},
        status.HTTP_403_FORBIDDEN: {"model": {}},
        status.HTTP_422_UNPROCESSABLE_ENTITY: {"model": ErrorsSchema},
    },
    operation_id="create-bed",
)
@remove_cache("Bed")
async def create_bed(
    payload: CreateBedSchema,
    service: BedService = Depends(),
) -> BedSchema:
    bed = await service.create_bed(payload)
    return bed


@api.post(
    "/bed/DeleteBed",
    responses={
        status.HTTP_204_NO_CONTENT: {"model": {}},
        status.HTTP_401_UNAUTHORIZED: {"model": {}},
        status.HTTP_403_FORBIDDEN: {"model": {}},
        status.HTTP_422_UNPROCESSABLE_ENTITY: {"model": ErrorsSchema},
    },
    operation_id="delete-bed",
)
@remove_cache("Bed")
async def delete_bed(
    payload: DeleteBedSchema,
    service: BedService = Depends(),
) -> Response:
    await service.delete_bed(payload.bed_id)
    return Response(status_code=status.HTTP_204_NO_CONTENT)


@api.post(
    "/bed/BatchUpdateBeds",
    responses={
        status.HTTP_200_OK: {"model": BedResourcesSchema},
        status.HTTP_401_UNAUTHORIZED: {"model": {}},
        status.HTTP_403_FORBIDDEN: {"model": {}},
        status.HTTP_422_UNPROCESSABLE_ENTITY: {"model": ErrorsSchema},
    },
    operation_id="batch-update-beds",
)
@remove_cache("Bed")
async def batch_update_beds(
    payload: BatchUpdateBedsSchema,
    service: BedService = Depends(),
) -> BedResourcesSchema:
    beds = await service.batch_update_beds(payload.beds)
    return beds


@api.post(
    "/bed/BatchDeleteBeds",
    responses={
        status.HTTP_204_NO_CONTENT: {"model": {}},
        status.HTTP_401_UNAUTHORIZED: {"model": {}},
        status.HTTP_403_FORBIDDEN: {"model": {}},
        status.HTTP_422_UNPROCESSABLE_ENTITY: {"model": ErrorsSchema},
    },
    operation_id="batch-delete-beds",
)
@remove_cache("Bed")
@remove_cache("BedGroup")
async def batch_delete_beds(
    payload: BatchDeleteBedSchema,
    service: BedService = Depends(),
) -> Response:
    await service.batch_delete_beds(payload.bed_ids)
    return Response(status_code=status.HTTP_204_NO_CONTENT)


@api.post(
    "/bed-group/BatchCreateBedGroups",
    responses={
        status.HTTP_200_OK: {"model": BedGroupResourcesSchema},
        status.HTTP_401_UNAUTHORIZED: {"model": {}},
        status.HTTP_403_FORBIDDEN: {"model": {}},
        status.HTTP_422_UNPROCESSABLE_ENTITY: {"model": ErrorsSchema},
    },
    operation_id="batch-create-bed-groups",
)
@remove_cache("BedGroup")
async def batch_create_bed_groups(
    payload: BatchCreateBedGroupsSchema,
    service: BedService = Depends(),
) -> BedGroupResourcesSchema:
    groups = await service.batch_create_bed_groups(payload.groups)
    return groups


@api.post(
    "/bed-group/BatchUpdateBedGroups",
    responses={
        status.HTTP_204_NO_CONTENT: {"model": {}},
        status.HTTP_401_UNAUTHORIZED: {"model": {}},
        status.HTTP_403_FORBIDDEN: {"model": {}},
        status.HTTP_422_UNPROCESSABLE_ENTITY: {"model": ErrorsSchema},
    },
    operation_id="batch-update-bed-groups",
)
@remove_cache("BedGroup")
async def batch_update_bed_groups(
    payload: BatchUpdateBedGroupsSchema,
    service: BedService = Depends(),
) -> Response:
    await service.batch_update_bed_groups(payload.groups)
    return Response(status_code=status.HTTP_204_NO_CONTENT)


@api.post(
    "/bed-group/BatchDeleteBedGroups",
    responses={
        status.HTTP_204_NO_CONTENT: {"model": {}},
        status.HTTP_401_UNAUTHORIZED: {"model": {}},
        status.HTTP_403_FORBIDDEN: {"model": {}},
        status.HTTP_422_UNPROCESSABLE_ENTITY: {"model": ErrorsSchema},
    },
    operation_id="batch-delete-bed-groups",
)
@remove_cache("BedGroup")
async def batch_delete_bed_groups(
    payload: BatchDeleteBedGroupsSchema,
    service: BedService = Depends(),
) -> Response:
    await service.batch_delete_bed_groups(payload.group_ids)
    return Response(status_code=status.HTTP_204_NO_CONTENT)


@api.post(
    "/bed-group/CreateBedGroup",
    responses={
        status.HTTP_200_OK: {"model": BedGroupSchema},
        status.HTTP_401_UNAUTHORIZED: {"model": {}},
        status.HTTP_403_FORBIDDEN: {"model": {}},
        status.HTTP_422_UNPROCESSABLE_ENTITY: {"model": ErrorsSchema},
    },
    operation_id="create-bed-group",
)
@remove_cache("BedGroup")
async def create_bed_group(
    payload: CreateBedGroupSchema,
    service: BedService = Depends(),
) -> BedGroupSchema:
    group = await service.create_bed_group(payload)
    return group


@api.post(
    "/bed-group/BatchAssignBeds",
    responses={
        status.HTTP_204_NO_CONTENT: {"model": {}},
        status.HTTP_401_UNAUTHORIZED: {"model": {}},
        status.HTTP_403_FORBIDDEN: {"model": {}},
        status.HTTP_422_UNPROCESSABLE_ENTITY: {"model": ErrorsSchema},
    },
    operation_id="batch-assign-beds",
)
@remove_cache("BedGroup")
async def batch_assign_beds(
    payload: BatchAssignBedsSchema, service: BedService = Depends()
) -> Response:
    for data in payload.resources:
        await service.batch_assign_beds(data.group_id, data.bed_ids)
    return Response(status_code=status.HTTP_204_NO_CONTENT)


@api.post(
    "/bed-group/AddBed",
    responses={
        status.HTTP_204_NO_CONTENT: {"model": {}},
        status.HTTP_401_UNAUTHORIZED: {"model": {}},
        status.HTTP_403_FORBIDDEN: {"model": {}},
        status.HTTP_422_UNPROCESSABLE_ENTITY: {"model": ErrorsSchema},
    },
    operation_id="add-bed-to-group",
)
@remove_cache("BedGroup")
async def add_bed_to_group(
    payload: AddBedToGroupSchema, service: BedService = Depends()
) -> Response:
    await service.add_bed_to_group(payload.group_id, payload.bed_id)
    return Response(status_code=status.HTTP_204_NO_CONTENT)


@api.post(
    "/bed-group/RemoveBed",
    responses={
        status.HTTP_204_NO_CONTENT: {"model": {}},
        status.HTTP_401_UNAUTHORIZED: {"model": {}},
        status.HTTP_403_FORBIDDEN: {"model": {}},
        status.HTTP_422_UNPROCESSABLE_ENTITY: {"model": ErrorsSchema},
    },
    operation_id="remove-bed-from-group",
)
@remove_cache("BedGroup")
async def remove_bed_from_group(
    payload: RemoveBedFromGroupSchema,
    service: BedService = Depends(),
) -> Response:
    await service.remove_bed_from_group(payload.group_id, payload.bed_id)
    return Response(status_code=status.HTTP_204_NO_CONTENT)


@api.post(
    "/bed-group/DeleteBedGroup",
    responses={
        status.HTTP_204_NO_CONTENT: {"model": {}},
        status.HTTP_401_UNAUTHORIZED: {"model": {}},
        status.HTTP_403_FORBIDDEN: {"model": {}},
        status.HTTP_422_UNPROCESSABLE_ENTITY: {"model": ErrorsSchema},
    },
    operation_id="delete-bed-group",
)
@remove_cache("BedGroup")
async def delete_bed_group(
    payload: DeleteBedGroupSchema,
    service: BedService = Depends(),
) -> Response:
    await service.delete_bed_group(payload.group_id)
    return Response(status_code=status.HTTP_204_NO_CONTENT)
