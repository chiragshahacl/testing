from src.proxy.client import DevicePlatformClient, HttpClient
from src.proxy.schemas import DeleteDeviceSchema


class ProxyService:
    async def delete_device(self, payload: DeleteDeviceSchema):
        token = HttpClient().get_token()
        device_client = DevicePlatformClient(token)

        device_client.delete_device(payload)
