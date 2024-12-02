from uuid import UUID

from fastapi import WebSocketException, status
from httpx import ConnectTimeout, HTTPStatusError

from src.common.clients.patient.http_client import PlatformHttpClient
from src.common.clients.patient.platform import PatientPlatformClient
from src.common.clients.patient.schemas import BedResourcesSchema


class PatientService:
    def __init__(self, auth_token: str):
        self.http_client = PlatformHttpClient(auth_token)
        self.patient_client = PatientPlatformClient(self.http_client)

    async def handle_beds_error(self, group_id: UUID) -> BedResourcesSchema:
        try:
            return await self.patient_client.get_beds_by_group_id(group_id)
        except HTTPStatusError as exc:
            raise WebSocketException(code=status.WS_1008_POLICY_VIOLATION) from exc
        except ConnectTimeout as exc:
            raise WebSocketException(code=status.WS_1013_TRY_AGAIN_LATER) from exc

    async def get_beds(self, group_id: UUID) -> BedResourcesSchema:
        """
        Get the list of beds for a given group id
        or raise a WebSocketException in case of error.

        Args:
            group_id: ID of the group to get beds for.

        Returns:
            BedResourcesSchema: A list of beds.

        Raises:
            WebSocketException 1008: In case of any HTTP status error.
            WebSocketException 1013: In case of TimeOut.
        """
        return await self.handle_beds_error(group_id)
