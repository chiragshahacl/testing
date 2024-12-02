import asyncio
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

import src.mllp.server as mllp_server
from src.admission.commands import api as admission_commands
from src.alarms.api import api as alarms_api
from src.broker import KafkaClient
from src.health_check.api import api as health_check_api
from src.mllp.api import api as mllp_api
from src.monitor.api import api as monitor_api
from src.monitor.commands import api as monitor_commands
from src.proxy.commands import api as proxy_api
from src.sensor.commands import api as sensor_commands
from src.settings import settings


@asynccontextmanager
async def lifespan(_: FastAPI):
    loop = asyncio.get_running_loop()
    loop.create_task(mllp_server.run())
    yield

    client = await KafkaClient()
    await client.stop()


def create_app() -> FastAPI:
    base_app = FastAPI(
        title="🦦",
        openapi_url=f"{settings.BASE_PATH}/openapi.json",
        docs_url=f"{settings.BASE_PATH}/docs",
        redoc_url=f"{settings.BASE_PATH}/redoc",
        swagger_ui_oauth2_redirect_url=f"{settings.BASE_PATH}/docs/oauth2-redirect",
        lifespan=lifespan,
    )
    base_app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.CORS_ORIGINS,
        allow_headers=["*"],
        allow_methods=["*"],
    )
    base_app.include_router(health_check_api, tags=["HealthCheck"])
    base_app.include_router(health_check_api, prefix=settings.BASE_PATH, tags=["HealthCheck"])
    base_app.include_router(alarms_api, prefix=settings.BASE_PATH, tags=["Alarms"])
    base_app.include_router(proxy_api, prefix=settings.BASE_PATH, tags=["Proxy"])
    base_app.include_router(sensor_commands, prefix=settings.BASE_PATH, tags=["Sensors"])
    base_app.include_router(monitor_api, prefix=settings.BASE_PATH, tags=["Monitor"])
    base_app.include_router(monitor_commands, prefix=settings.BASE_PATH, tags=["Monitor"])
    base_app.include_router(admission_commands, prefix=settings.BASE_PATH, tags=["Admission"])
    base_app.include_router(mllp_api, prefix=settings.BASE_PATH, tags=["MLLP"])
    return base_app


app = create_app()
