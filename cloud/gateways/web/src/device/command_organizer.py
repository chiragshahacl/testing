import asyncio
from datetime import datetime, timedelta
from typing import Optional
from uuid import UUID

from fastapi import Depends

from src.common.exceptions import BaseValidationException
from src.common.schemas import base as common_schemas
from src.event_sourcing.events import CommandExecutionRequestEvent
from src.event_sourcing.schemas import CommandResponseEventState


class DeviceConnectionFailure(BaseValidationException):
    def __init__(self) -> None:
        self.error = common_schemas.ErrorSchema(
            loc=["body", "id"],
            msg="Could not connect with device.",
            type="connection_error.failed_to_connect",
        )


class CommandOrganizer:
    _instance = None

    def __new__(cls, *args, **kwargs):
        if not cls._instance:
            cls._instance = super(CommandOrganizer, cls).__new__(cls, *args, **kwargs)
        return cls._instance

    def __init__(self, event_stream: CommandExecutionRequestEvent = Depends()) -> None:
        self.event_stream = event_stream
        if not hasattr(self, "initialized"):
            self.responses = {}
            self.blacklist = set()
            self.initialized = True

    def add_request(self, request_id: UUID) -> None:
        self.responses[request_id] = None
        if request_id in self.blacklist:
            self.blacklist.remove(request_id)

    def add_response(self, response: CommandResponseEventState) -> None:
        if response.request_id not in self.blacklist:
            self.responses[response.request_id] = response

    def check_for_response(self, request_id: UUID) -> Optional[CommandResponseEventState]:
        return self.responses.pop(request_id, None)

    def blacklist_request(self, request_id: UUID) -> None:
        self.blacklist.add(request_id)


async def wait_for_device_response(request_id: UUID) -> CommandResponseEventState:
    organizer = CommandOrganizer()
    max_timeout = datetime.now() + timedelta(seconds=30)
    while datetime.now() <= max_timeout:
        response = organizer.check_for_response(request_id)
        if response is None:
            await asyncio.sleep(0.05)
        else:
            return response
    organizer.blacklist_request(request_id)
    raise DeviceConnectionFailure
