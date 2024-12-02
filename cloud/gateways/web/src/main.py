import asyncio
from contextlib import asynccontextmanager

import httpx
import sentry_sdk
from fastapi import Depends, FastAPI
from fastapi.encoders import jsonable_encoder
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, PlainTextResponse
from healthcheck import KafkaHealthcheckService
from sentry_sdk.integrations.fastapi import FastApiIntegration
from sentry_sdk.integrations.httpx import HttpxIntegration
from sentry_sdk.integrations.starlette import StarletteIntegration
from starlette import status
from starlette.requests import Request

from src.audit.api import api as audit_trail_api
from src.auth.api import api as auth_api
from src.auth.dependencies import InternalAuthRequired
from src.bed.api import api as bed_api
from src.bed_group.api import api as bed_group_api
from src.common.exceptions import BaseValidationException
from src.common.schemas import ErrorsSchema
from src.config.api import api as config_api
from src.consumer import KafkaConsumerFactory, event_consumer
from src.device.api import api as device_api
from src.event_sourcing.publisher import KafkaProducerFactory
from src.health_check.api import api as health_check_api
from src.middleware import CorrelationIDMiddleware
from src.patient.api import api as patient_api
from src.settings import settings

sentry_sdk.init(
    dsn=settings.SENTRY_DSN,
    traces_sample_rate=settings.SENTRY_TRACE_SAMPLE_RATE,
    debug=settings.DEBUG,
    environment=settings.ENVIRONMENT,
    release=settings.SIBEL_VERSION,
    profiles_sample_rate=settings.SENTRY_PROFILES_SAMPLE_RATE,
    integrations=[
        StarletteIntegration(),
        FastApiIntegration(),
        HttpxIntegration(),
    ],
)


@asynccontextmanager
async def app_lifespan(_: FastAPI):  # pylint: disable=W0621,W0613
    loop = asyncio.get_running_loop()
    producer_client = await KafkaProducerFactory()()
    consumer_client = await KafkaConsumerFactory()()
    await KafkaHealthcheckService().start()
    task = loop.create_task(KafkaHealthcheckService().watchdog(event_consumer, consumer_client))
    yield
    task.cancel()
    await producer_client.stop()
    await consumer_client.stop()


async def validation_error_handler(_: Request, exc: BaseValidationException):
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content=jsonable_encoder(ErrorsSchema(detail=[exc.error])),
    )


async def http_exception_handler(_: Request, exc: httpx.HTTPStatusError):
    if exc.response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY:
        return JSONResponse(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            content=exc.response.json(),
        )
    if exc.response.status_code in [
        status.HTTP_401_UNAUTHORIZED,
        status.HTTP_403_FORBIDDEN,
    ]:
        return PlainTextResponse(status_code=exc.response.status_code)
    raise exc


def create_app() -> FastAPI:
    base_app = FastAPI(
        debug=settings.DEBUG,
        openapi_url=f"{settings.BASE_PATH}/openapi.json",
        docs_url=f"{settings.BASE_PATH}/docs",
        redoc_url=f"{settings.BASE_PATH}/redoc",
        swagger_ui_oauth2_redirect_url=f"{settings.BASE_PATH}/docs/oauth2-redirect",
        lifespan=app_lifespan,
    )
    base_app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.CORS_ORIGINS,
        allow_headers=["*"],
        allow_methods=["*"],
    )
    base_app.add_middleware(CorrelationIDMiddleware)
    base_app.add_exception_handler(BaseValidationException, validation_error_handler)
    base_app.add_exception_handler(httpx.HTTPStatusError, http_exception_handler)
    base_app.include_router(health_check_api, tags=["System"])
    base_app.include_router(health_check_api, prefix=settings.BASE_PATH, tags=["System"])
    base_app.include_router(auth_api, prefix=settings.BASE_PATH, tags=["Authentication"])
    base_app.include_router(
        patient_api,
        prefix=settings.BASE_PATH,
        dependencies=[Depends(InternalAuthRequired())],
        tags=["Patient"],
    )
    base_app.include_router(
        bed_api,
        prefix=settings.BASE_PATH,
        dependencies=[Depends(InternalAuthRequired())],
        tags=["Bed"],
    )
    base_app.include_router(
        bed_group_api,
        prefix=settings.BASE_PATH,
        dependencies=[Depends(InternalAuthRequired())],
        tags=["BedGroup"],
    )
    base_app.include_router(
        audit_trail_api,
        prefix=settings.BASE_PATH,
        dependencies=[Depends(InternalAuthRequired())],
        tags=["AuditTrail"],
    )
    base_app.include_router(
        device_api,
        prefix=settings.BASE_PATH,
        dependencies=[Depends(InternalAuthRequired())],
        tags=["Device"],
    )
    base_app.include_router(
        config_api,
        prefix=settings.BASE_PATH,
        dependencies=[Depends(InternalAuthRequired())],
        tags=["Configuration"],
    )
    return base_app


app = create_app()
