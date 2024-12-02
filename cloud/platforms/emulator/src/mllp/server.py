# pylint: skip-file

import asyncio
from collections import deque
from datetime import datetime
from typing import Collection

from hl7.mllp import start_hl7_server
from loguru import logger

from src.mllp.schemas import MLLPMessage
from src.settings import settings

mllp_buffer: Collection[MLLPMessage] = deque(maxlen=settings.MLLP_QUEUE_SIZE)


async def run():
    logger.info(f"Starting MLLP server on {settings.MLLP_SERVER_PORT}")
    try:
        async with await start_hl7_server(
            process_hl7_messages, port=settings.MLLP_SERVER_PORT
        ) as hl7_server:
            await hl7_server.serve_forever()
    except asyncio.CancelledError:
        logger.info("Cancelled corutine")
    except Exception:  # pylint: disable=broad-exception-caught
        logger.info("Error occurred in main")


DB = [
    {
        "primary_patient_id": "123",
        "dob": "19700101",
        "family_name": "Doe",
        "gender": "M",
        "given_name": "John",
    },
    {
        "primary_patient_id": "456",
        "dob": "19200101",
        "family_name": "Doe",
        "gender": "F",
        "given_name": "Jane",
        "multiple_records": True,
    },
    {
        "primary_patient_id": "789",
        "dob": "19300101",
        "family_name": "Doe",
        "gender": "F",
        "given_name": "Jane",
    },
    {
        "primary_patient_id": "001",
        "dob": "20120101",
        "family_name": "Smith",
        "gender": "M",
        "given_name": "Robert",
    },
    {
        "primary_patient_id": "002",
        "dob": "20130101",
        "family_name": "Doe",
        "gender": "M",
        "given_name": "John",
    },
    {
        "primary_patient_id": "003",
        "dob": "20150101",
        "family_name": "Doe",
        "gender": "F",
        "given_name": "Jane",
    },
    {
        "primary_patient_id": "004",
        "dob": "20090101",
        "family_name": "Doe",
        "gender": "M",
        "given_name": "John",
    },
]


def find_patient(primary_patient_id=None, given_name=None, family_name=None, dob=None):
    result = []

    if primary_patient_id:
        logger.info(f"Searching by patient_id {primary_patient_id}")
        result = [x for x in DB if x["primary_patient_id"] == primary_patient_id]
    elif given_name and family_name:
        logger.info(f"Searching by given_name {given_name} and family_name {family_name}")
        result = [
            x for x in DB if x["given_name"] == given_name and x["family_name"] == family_name
        ]

    if dob:
        logger.info(f"And by dob {dob}")
        result = [x for x in result if x["dob"] == dob]

    return result


def generate_k22(message):
    current_date = datetime.now().strftime("%Y%m%d%H%M%S")

    message_control_id = message[0][10][0]
    query_tag = message[1][2][0]

    # pylint: disable=line-too-long
    hl7_message = (
        f"MSH|^~\&|SendingApp|SendingFac|ReceivingApp|ReceivingFac|{current_date}||RSP^K22|{message_control_id}|P|2.6|\n"  # noqa
        f"MSA|AA|{message_control_id}|\n"
        f"QAK|{query_tag}|OK|\n"
    )
    hl7_message += str(message[1]) + "\n"

    try:
        if "PID" in message[1][3][0][0][0]:
            primary_patient_id = message[1][3][0][1][0]
            given_name = None
            family_name = None
            dob = None
        else:
            primary_patient_id = None
            given_name = message[1][3][0][0][0]
            family_name = message[1][3][0][1][0]
            dob = message[1][3][0][2][0] if len(message[1][3][0]) == 3 else None
    except Exception:
        given_name = None
        family_name = None
        dob = None
        primary_patient_id = None

    for index, patient in enumerate(
        find_patient(
            primary_patient_id=primary_patient_id,
            family_name=family_name,
            given_name=given_name,
            dob=dob,
        )
    ):
        given_name = patient["given_name"]
        family_name = patient["family_name"]
        dob = patient["dob"]
        gender = patient["gender"]
        identifier = patient["primary_patient_id"]

        medical_record = f"{identifier}^^^SibelHealth^MR"

        if patient.get("multiple_records"):
            medical_record += f"~{identifier}-2^^^OtherHospital^MR"

        hl7_message += (
            f"PID|{index + 1}||{medical_record}||{family_name}^{given_name}||{dob}|{gender}|||\n"  # noqa
        )

    return hl7_message


async def process_hl7_messages(hl7_reader, hl7_writer):
    peername = hl7_writer.get_extra_info("peername")
    logger.info(f"Connection established {peername}")
    try:
        while not hl7_writer.is_closing():
            message = await hl7_reader.readmessage()
            content = str(message).replace("\r", "\n")
            logger.info("Received message:\n", content)
            response = handle_message(message)
            logger.info("Responding with message:\n", response)
            hl7_writer.writemessage(response)
            message = MLLPMessage(content=content)
            mllp_buffer.append(message)
            await hl7_writer.drain()
    except asyncio.IncompleteReadError:
        if not hl7_writer.is_closing():
            hl7_writer.close()
            await hl7_writer.wait_closed()
    logger.info(f"Connection closed {peername}")


def handle_message(message):
    message_type = message.segment("MSH").extract_field(1, 9)

    match message_type:
        case "QBP":
            return generate_k22(message)
        case "ORU":
            return message.create_ack()
        case _:
            raise RuntimeError(f"Unsupported message {message_type}")
