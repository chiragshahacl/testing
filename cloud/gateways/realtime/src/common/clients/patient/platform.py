import abc
from uuid import UUID

from httpx import Response

from src.common.clients.patient.http_client import PlatformHttpClient
from src.common.clients.patient.schemas import BedResourcesSchema
from src.settings import config


class PlatformInterface(abc.ABC):
    def __init__(self, client: PlatformHttpClient):
        self.client = client

    @property
    @abc.abstractmethod
    def root_url(self) -> str:
        """Abstract property, override"""

    async def get(self, endpoint: str) -> Response:
        async with self.client() as client:
            return await client.get(f"{self.root_url}{endpoint}")


class PatientPlatformClient(PlatformInterface):
    root_url: str = f"{config.WEB_BASE_URL}"

    async def get_beds_by_group_id(self, group_id: UUID) -> BedResourcesSchema:
        response = await self.get(f"/bed-group/{group_id}/beds")
        response.raise_for_status()
        return BedResourcesSchema(**response.json())
