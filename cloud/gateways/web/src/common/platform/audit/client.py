from typing import Optional
from uuid import UUID

from starlette import status

from src.common.platform.audit.schemas import PlatformAuditResources
from src.common.platform.common.http_base import BaseClient
from src.settings import settings


class AuditPlatformClient(BaseClient):
    root_url: str = f"{settings.AUDIT_PLATFORM_BASE_URL}"

    async def get_audit_list(self, entity_id: UUID) -> Optional[PlatformAuditResources]:
        response = await self.client.get(f"{self.root_url}/{entity_id}")
        if response.status_code == status.HTTP_404_NOT_FOUND:
            return None

        response.raise_for_status()
        return PlatformAuditResources.model_validate_json(response.text)
