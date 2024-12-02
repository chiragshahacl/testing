from typing import AsyncGenerator

import httpx
from starlette.requests import Request


class PlatformHttpClient:
    async def __call__(
        self,
        request: Request,
    ) -> AsyncGenerator[httpx.AsyncClient, None]:
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {request.state.internal_token}",
            "x-correlation-id": request.state.correlation_id,
        }
        async with httpx.AsyncClient(headers=headers) as client:
            yield client
