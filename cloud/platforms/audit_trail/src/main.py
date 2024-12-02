import asyncio
from contextlib import asynccontextmanager
from typing import List

import sentry_sdk
from fastapi import Depends, FastAPI
from fastapi.encoders import jsonable_encoder
from healthcheck import KafkaHealthcheckService
from starlette import status
from starlette.middleware import Middleware
from starlette.requests import Request
from starlette.responses import JSONResponse

from src.audit.api import api as audit_trail_api
from src.audit.consumer import internal_audit_trail_consumer
from src.common.dependencies import InternalAuthRequired
from src.common.exceptions import BaseValidationException
from src.common.schemas import ErrorsSchema
from src.health_check.api import api as health_check_api
from src.settings import settings

THIRD_PARTY_MIDDLEWARE: List[Middleware] = []
CUSTOM_MIDDLEWARE: List[Middleware] = []
EFFECTIVE_MIDDLEWARE: List[Middleware] = THIRD_PARTY_MIDDLEWARE + CUSTOM_MIDDLEWARE


sentry_sdk.init(
    dsn=settings.SENTRY_DSN,
    traces_sample_rate=settings.SENTRY_TRACE_SAMPLE_RATE,
    debug=settings.DEBUG,
    environment=settings.ENVIRONMENT,
    release=settings.SIBEL_VERSION,
    profiles_sample_rate=settings.SENTRY_PROFILES_SAMPLE_RATE,
)


async def validation_error_handler(_: Request, exc: BaseValidationException) -> JSONResponse:
    error = exc.error
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content=jsonable_encoder(ErrorsSchema(detail=[error])),
    )


@asynccontextmanager
async def lifespan(_: FastAPI):
    loop = asyncio.get_running_loop()
    await KafkaHealthcheckService().start()
    task = loop.create_task(KafkaHealthcheckService().watchdog(internal_audit_trail_consumer))

    yield

    task.cancel()


def create_app() -> FastAPI:
    base_app = FastAPI(
        openapi_url=f"{settings.BASE_PATH}/openapi.json",
        docs_url=f"{settings.BASE_PATH}/docs",
        redoc_url=f"{settings.BASE_PATH}/redoc",
        swagger_ui_oauth2_redirect_url=f"{settings.BASE_PATH}/docs/oauth2-redirect",
        lifespan=lifespan,
    )
    base_app.add_exception_handler(BaseValidationException, validation_error_handler)
    base_app.include_router(health_check_api)
    base_app.include_router(
        audit_trail_api, dependencies=[Depends(InternalAuthRequired())], tags=["REST"]
    )
    return base_app


app = create_app()
