from contextlib import asynccontextmanager

from fastapi import Depends, FastAPI
from fastapi.encoders import jsonable_encoder
from healthcheck import KafkaHealthcheckService
from starlette import status
from starlette.requests import Request
from starlette.responses import JSONResponse

from app.common.dependencies import InternalAuthRequired
from app.common.event_sourcing.publisher import KafkaProducerClient
from app.common.exceptions import BaseValidationException
from app.common.schemas import ErrorsSchema
from app.config.api import api as config_rest_api
from app.config.commands import api as config_commands
from app.health_check.api import api as health_check_api
from app.settings import config


async def validation_error_handler(_: Request, exc: BaseValidationException) -> JSONResponse:
    error = exc.error
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content=jsonable_encoder(ErrorsSchema(detail=[error])),
    )


@asynccontextmanager
async def lifespan(_: FastAPI):
    producer_client = await KafkaProducerClient()

    await KafkaHealthcheckService().start()

    yield

    await producer_client.stop()


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
    base_app.include_router(health_check_api, tags=["Config REST"])
    base_app.include_router(
        config_commands,
        dependencies=[Depends(InternalAuthRequired())],
        tags=["Config Commands"],
    )
    base_app.include_router(
        config_rest_api,
        dependencies=[Depends(InternalAuthRequired())],
        tags=["Config REST API"],
    )
    return base_app


app = create_app()
