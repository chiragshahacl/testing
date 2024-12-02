from typing import Optional

import httpx
from fastapi import Depends

from src.audit import schemas as web_audit_schemas
from src.common.dependencies import PlatformHttpClient
from src.common.platform.audit.client import AuditPlatformClient


class AuditService:
    def __init__(self, http_client: httpx.AsyncClient = Depends(PlatformHttpClient())):
        self.http_client = http_client
        self.audit_client = AuditPlatformClient(self.http_client)

    async def get_audit_list(self, entity_id) -> Optional[web_audit_schemas.WebAuditResources]:
        platform_audit_resources = await self.audit_client.get_audit_list(entity_id)
        if not platform_audit_resources:
            return None

        return web_audit_schemas.WebAuditResources.from_platform(platform_audit_resources)
