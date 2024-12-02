from src.device.command_organizer import CommandOrganizer
from src.event_sourcing.schemas import IncomingDeviceCommandResponseSchema


async def process_device_commands_responses(
    message: IncomingDeviceCommandResponseSchema,
):
    organizer = CommandOrganizer()
    organizer.add_response(message.event_state)
