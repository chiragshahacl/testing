import asyncio
from contextlib import asynccontextmanager

import sentry_sdk
from fastapi import Depends, FastAPI
from fastapi.encoders import jsonable_encoder
from healthcheck import KafkaHealthcheckService
from sentry_sdk import configure_scope, push_scope
from starlette import status
from starlette.requests import Request
from starlette.responses import JSONResponse

from app.bed.api import api as bed_api
from app.bed.commands import api as bed_commands
from app.common.dependencies import InternalAuthRequired
from app.common.event_sourcing.publisher import KafkaProducerClient
from app.common.exceptions import BaseValidationException
from app.common.schemas import ErrorsSchema
from app.common.utils import ScopeConfiguration
from app.consumer import KafkaConsumerClient, event_consumer
from app.device.src.device.api import api as device_apis
from app.device.src.device.commands import api as device_commands
from app.encounter.commands import api as encounter_commands
from app.event_subscriptions import register_event_subscriptions
from app.health_check.api import api as health_check_api
from app.patient.api import api as patient_api
from app.patient.commands import api as patient_commands
from app.settings import config

sentry_sdk.init(
    dsn=config.SENTRY_DSN,
    traces_sample_rate=config.SENTRY_TRACE_SAMPLE_RATE,
    debug=config.DEBUG,
    environment=config.ENVIRONMENT,
    release=config.SIBEL_VERSION,
    profiles_sample_rate=config.SENTRY_PROFILES_SAMPLE_RATE,
    enable_tracing=config.ENVIRONMENT != "local",
)


async def add_correlation_id(request: Request, call_next):
    with push_scope() as scope:
        correlation_id = request.headers.get("x-correlation-id")
        if correlation_id:
            configure_scope(ScopeConfiguration(scope, correlation_id)())
            request.state.correlation_id = correlation_id
        response = await call_next(request)
        return response


async def validation_error_handler(_: Request, exc: BaseValidationException) -> JSONResponse:
    error = exc.error
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content=jsonable_encoder(ErrorsSchema(detail=[error])),
    )


@asynccontextmanager
async def lifespan(_: FastAPI):
    loop = asyncio.get_running_loop()
    register_event_subscriptions()
    producer_client = await KafkaProducerClient()
    consumer_client = await KafkaConsumerClient()

    await KafkaHealthcheckService().start()

    consumer_task = loop.create_task(
        KafkaHealthcheckService().watchdog(event_consumer, consumer_client)
    )

    yield

    consumer_task.cancel()
    await producer_client.stop()
    await consumer_client.stop()


def create_app() -> FastAPI:
    base_app = FastAPI(
        debug=config.DEBUG,
        openapi_url=f"{config.BASE_PATH}/openapi.json",
        docs_url=f"{config.BASE_PATH}/docs",
        redoc_url=f"{config.BASE_PATH}/redoc",
        swagger_ui_oauth2_redirect_url=f"{config.BASE_PATH}/docs/oauth2-redirect",
        lifespan=lifespan,
    )
    base_app.add_exception_handler(BaseValidationException, validation_error_handler)
    base_app.middleware("http")(add_correlation_id)
    base_app.include_router(health_check_api, tags=["Patient REST"])
    base_app.include_router(
        patient_api,
        dependencies=[Depends(InternalAuthRequired())],
        tags=["Patient REST"],
    )
    base_app.include_router(
        patient_commands,
        dependencies=[Depends(InternalAuthRequired())],
        tags=["Patient Commands"],
    )
    base_app.include_router(
        bed_commands,
        prefix=config.BASE_PATH,
        dependencies=[Depends(InternalAuthRequired())],
        tags=["Patient Commands"],
    )

    base_app.include_router(
        encounter_commands,
        prefix=config.BASE_PATH,
        dependencies=[Depends(InternalAuthRequired())],
        tags=["Patient Commands"],
    )
    base_app.include_router(
        bed_api,
        prefix=config.BASE_PATH,
        dependencies=[Depends(InternalAuthRequired())],
        tags=["Patient REST"],
    )
    base_app.include_router(
        device_apis,
        dependencies=[Depends(InternalAuthRequired())],
        prefix="/device",
        tags=["Device REST"],
    )
    base_app.include_router(
        device_commands,
        dependencies=[Depends(InternalAuthRequired())],
        prefix="/device",
        tags=["Device Commands"],
    )
    base_app.include_router(
        encounter_commands,
        dependencies=[Depends(InternalAuthRequired())],
        prefix=config.BASE_PATH,
    )
    return base_app


app = create_app()
