from fastapi import APIRouter, Depends
from starlette import status
from starlette.responses import Response

from src.proxy.schemas import DeleteDeviceSchema
from src.proxy.services import ProxyService

api = APIRouter()


@api.post(
    "/proxy/device/command/DeleteDevice",
    responses={
        status.HTTP_204_NO_CONTENT: {"model": {}},
    },
    operation_id="delete-device-command",
)
async def delete_device_command(
    payload: DeleteDeviceSchema,
    service: ProxyService = Depends(),
) -> Response:
    await service.delete_device(payload)
    return Response(status_code=204)
