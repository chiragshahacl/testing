from httpx import AsyncClient


class PlatformHttpClient:
    def __init__(self, auth_token: str):
        self.headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {auth_token}",
        }

    def __call__(self) -> AsyncClient:
        return AsyncClient(headers=self.headers)
