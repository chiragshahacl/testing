import asyncio
from contextlib import asynccontextmanager

import sentry_sdk
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from healthcheck import KafkaHealthcheckService

from src.cache import MetricsCacheService
from src.common.enums import HeaderEventTypes
from src.health_check.api import api as health_check_api
from src.realtime.api import api as real_time_api
from src.realtime.subscriber import ConnectionManager
from src.settings import config
from src.streams import EventSubscriber, KafkaClient, broker_consumer

if config.SENTRY_DSN.get_secret_value():
    sentry_sdk.init(
        dsn=config.SENTRY_DSN.get_secret_value(),
        traces_sample_rate=config.SENTRY_TRACE_SAMPLE_RATE,
        debug=config.DEBUG,
        environment=config.ENVIRONMENT,
        release=config.SIBEL_VERSION,
        profiles_sample_rate=config.SENTRY_PROFILES_SAMPLE_RATE,
    )

DESCRIPTION = """
Documentation for real-time process can be found
[here](https://github.com/sibelhealth/tucana/tree/main/cloud/gateways/realtime/src/realtime/README.md)
"""


NOTIFY_TOPICS = {
    config.BROKER_TOPIC_VITALS,
    config.BROKER_TOPIC_ALERTS,
    config.BROKER_TOPIC_SDC_EVENTS,
}
BROADCAST_TOPICS = {
    config.BROKER_TOPIC_PATIENTS,
    config.BROKER_TOPIC_DEVICES,
    config.BROKER_TOPIC_SDC_REALTIME_STATE,
}


def register_event_listeners():
    # create clients
    sub_manager = ConnectionManager()
    event_subscriber = EventSubscriber()
    cache_service = MetricsCacheService()

    # register event handlers
    event_subscriber.register_multi_topic_handler(list(BROADCAST_TOPICS), sub_manager.broadcast)
    event_subscriber.register_multi_topic_handler(list(NOTIFY_TOPICS), sub_manager.notify)

    # cache incoming metrics
    event_subscriber.register_event_type_handler(
        HeaderEventTypes.NEW_METRICS, cache_service.new_metrics_handler
    )
    event_subscriber.register_event_type_handler(
        HeaderEventTypes.SENSOR_REMOVED_EVENT, cache_service.sensor_removed_handler
    )


@asynccontextmanager
async def app_lifespan(_: FastAPI):  # pylint: disable=W0621,W0613
    task = None
    loop = asyncio.get_running_loop()
    client = await KafkaClient()
    await KafkaHealthcheckService().start()

    try:
        register_event_listeners()
        # start consumer
        task = loop.create_task(KafkaHealthcheckService().watchdog(broker_consumer, client))

        yield
    finally:
        if task:
            task.cancel()


def create_app() -> FastAPI:
    base_app = FastAPI(
        title="🦦",
        description=DESCRIPTION,
        openapi_url=f"{config.BASE_PATH}/openapi.json",
        docs_url=f"{config.BASE_PATH}/docs",
        redoc_url=f"{config.BASE_PATH}/redoc",
        swagger_ui_oauth2_redirect_url=f"{config.BASE_PATH}/docs/oauth2-redirect",
        lifespan=app_lifespan,
    )
    base_app.add_middleware(
        CORSMiddleware,
        allow_origins=config.CORS_ORIGINS,
        allow_headers=["*"],
        allow_methods=["*"],
    )
    base_app.include_router(health_check_api)
    base_app.include_router(health_check_api, prefix=config.BASE_PATH)
    base_app.include_router(real_time_api, prefix=config.BASE_PATH)

    return base_app


app = create_app()
