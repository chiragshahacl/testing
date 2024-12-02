from typing import List

import httpx
from loguru import logger

from src.proxy.schemas import DeleteDeviceSchema, DeviceSchema
from src.settings import settings


class HttpClient:
    def __init__(self):
        self.headers = {"Content-Type": "application/json"}
        self.client = httpx.Client(headers=self.headers)

    def get_token(self) -> str:
        logger.info("Authenticating client")
        response = self.client.post(
            f"{settings.WEB_GATEWAY_URL}/auth/token",
            json={
                "username": settings.ADMIN_USERNAME,
                "password": settings.ADMIN_PASSWORD,
            },
        )
        response.raise_for_status()
        return response.json()["access"]


class InternalClient(HttpClient):
    def __init__(self, token: str):
        super().__init__()
        self.headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {token}",
        }
        self.client = httpx.Client(headers=self.headers)


class DevicePlatformClient(InternalClient):
    def get_devices(self) -> List[DeviceSchema]:
        response = self.client.get(f"{settings.DEVICE_PLATFORM_URL}")
        response.raise_for_status()
        return [DeviceSchema(**d) for d in response.json()["resources"]]

    def create_device(self, device: DeviceSchema) -> None:
        response = self.client.post(
            f"{settings.DEVICE_PLATFORM_URL}/CreateDevice",
            content=device.json(),
        )
        response.raise_for_status()

    def delete_device(self, device: DeleteDeviceSchema) -> None:
        response = self.client.post(
            f"{settings.DEVICE_PLATFORM_URL}/DeleteDevice",
            content=device.json(),
        )
        response.raise_for_status()

    def update_device(self, device: DeviceSchema) -> None:
        response = self.client.post(
            f"{settings.DEVICE_PLATFORM_URL}/UpdateDevice",
            content=device.json(),
        )
        response.raise_for_status()

    def upsert_devices(self, devices: List[DeviceSchema]) -> None:
        found_devices = {d.id: d for d in self.get_devices()}
        for device in devices:
            logger.info(f"Upserting device: {device.dict()}")
            if device.id not in found_devices:
                self.create_device(device)
            else:
                self.update_device(device)
