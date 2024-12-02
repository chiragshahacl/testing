from fastapi import APIRouter, Depends, HTTPException
from starlette import status

from src.audit import schemas as audit_trail_schemas
from src.audit.services import AuditTrailService
from src.settings import settings

api = APIRouter(prefix=settings.BASE_PATH)


@api.get(
    "/{entity_id}",
    responses={
        status.HTTP_200_OK: {"model": audit_trail_schemas.InternalAuditEventResources},
        status.HTTP_401_UNAUTHORIZED: {"model": {}},
        status.HTTP_403_FORBIDDEN: {"model": {}},
        status.HTTP_404_NOT_FOUND: {"model": {}},
    },
    operation_id="get-audit-trail",
)
async def get_audit_trail(
    entity_id: str, audit_trail_service: AuditTrailService = Depends()
) -> audit_trail_schemas.InternalAuditEventResources:
    internal_audit_events = await audit_trail_service.get_audit_trail(entity_id)
    if not internal_audit_events:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)
    return internal_audit_events
