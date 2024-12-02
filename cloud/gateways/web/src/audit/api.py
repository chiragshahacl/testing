from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException
from starlette import status

from src.audit import schemas as web_audit_schemas
from src.audit import services as audit_services
from src.common.responses import FastJSONResponse
from src.common.schemas import base as common_schemas

api = APIRouter()


@api.get(
    "/audit/{entity_id:uuid}",
    responses={
        status.HTTP_200_OK: {"model": web_audit_schemas.WebAuditResources},
        status.HTTP_401_UNAUTHORIZED: {"model": {}},
        status.HTTP_403_FORBIDDEN: {"model": {}},
        status.HTTP_422_UNPROCESSABLE_ENTITY: {"model": common_schemas.ErrorSchema},
    },
    operation_id="get-audit-list",
    response_class=FastJSONResponse,
)
async def get_audit_list(
    entity_id: UUID,
    audit_service: audit_services.AuditService = Depends(),
) -> FastJSONResponse:
    audit_list = await audit_service.get_audit_list(entity_id)
    if not audit_list:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)
    return FastJSONResponse(audit_list)
