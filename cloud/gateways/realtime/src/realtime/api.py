from typing import Annotated

from fastapi import APIRouter, Depends
from loguru import logger
from starlette.websockets import WebSocket

from src.cache import MetricsCacheService
from src.realtime.authentication import get_token
from src.realtime.schemas import WSSubscription
from src.realtime.subscriber import (
    ConnectionManager,
    PatientsConnection,
    PatientsSubscription,
)

api = APIRouter()
cache_service = MetricsCacheService()


async def send_cached_vitals(wsocket: WebSocket, patient_identifiers: list[str]):
    for patient_identifier in patient_identifiers:
        for message in cache_service.get_cached_metrics(patient_identifier):
            logger.debug(f"Returning cached metrics: {message}")
            await wsocket.send_text(message)


@api.websocket("/vitals")
async def vitals_consumer(
    wsocket: WebSocket,
    token: Annotated[str, Depends(get_token)],
):
    connection_manager = ConnectionManager()

    await wsocket.accept()

    # subscribe to incoming events
    connection = PatientsConnection(wsocket, PatientsSubscription([]))
    connection_manager.subscribe(connection)

    # wait for new filters
    async for message in wsocket.iter_json():
        parsed_message = WSSubscription(**message)
        logger.info(f"Setting filtering for {connection} to: {parsed_message}")
        if parsed_message.send_cache:
            await send_cached_vitals(
                wsocket=wsocket, patient_identifiers=parsed_message.patient_identifiers
            )
        connection.update_channels(parsed_message.patient_identifiers)
        connection.update_filters(parsed_message.filters.to_filters())

    # remove all ongoing connections
    connection_manager.unsubscribe(connection)
