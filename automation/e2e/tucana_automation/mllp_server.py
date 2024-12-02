from datetime import datetime
from functools import partial
from enum import Enum
import typer
import aiorun
import asyncio

from hl7.mllp import start_hl7_server

PORT = 2575


class ACKCode(str, Enum):
    AA = "AA"  # Application Accepted
    AR = "AR"  # Application Rejected
    AE = "AE"  # Application Errored
    CA = "CA"  # Commit Accepted
    CR = "CR"  # Commit Rejected
    CE = "CE"  # Commit Errored


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
    },
    {
        "primary_patient_id": "789",
        "dob": "19300101",
        "family_name": "Doe",
        "gender": "F",
        "given_name": "Jane",
    },
]


def find_patient(primary_patient_id=None, given_name=None, family_name=None, dob=None):
    result = []

    if primary_patient_id:
        result = [x for x in DB if x["primary_patient_id"]
                  == primary_patient_id]
    elif given_name and family_name:
        result = [
            x
            for x in DB
            if x["given_name"] == given_name and x["family_name"] == family_name
        ]

    if dob:
        result = [x for x in result if x["dob"] == dob]

    return result


def generate_k22(message, ack_code, invalid_response):
    current_date = datetime.now().strftime("%Y%m%d%H%M%S")

    message_control_id = message[0][10][0]
    query_tag = message[1][2][0]

    # pylint: disable=line-too-long
    hl7_message = (
        f"MSH|^~\&|SendingApp|SendingFac|ReceivingApp|ReceivingFac|{current_date}||RSP^K22|{message_control_id}|P|2.6|\n"
        f"MSA|{ack_code}|{message_control_id}|\n"
        f"QAK|{query_tag}|OK|\n"
    )

    if invalid_response:
        # invalid response means headers but no patients
        return hl7_message

    hl7_message += str(message[1]) + "\n"

    try:
        if "PID" in message[1][3][0][0][0]:
            primary_patient_id = message[1][3][0][1][0]
            given_name = None
            family_name = None
        else:
            primary_patient_id = None
            given_name = message[1][3][0][0][0]
            family_name = message[1][3][0][1][0]
    except Exception:
        given_name = None
        family_name = None
        primary_patient_id = None

    for patient in find_patient(
        primary_patient_id=primary_patient_id,
        family_name=family_name,
        given_name=given_name,
    ):
        given_name = patient["given_name"]
        family_name = patient["family_name"]
        dob = patient["dob"]
        gender = patient["gender"]
        identifier = patient["primary_patient_id"]

        hl7_message += f"PID|1||{identifier}^^^SibelHealth^MR||{family_name}^{given_name}||{dob}|{gender}|||\n"  # noqa

    return hl7_message


async def process_hl7_messages(
    hl7_reader, hl7_writer, ack_code=None, timeout=None, skip_response=None, invalid_response=None, empty_response=None
):
    peername = hl7_writer.get_extra_info("peername")
    print(f"Connection established {peername}")
    try:
        while not hl7_writer.is_closing():
            message = await hl7_reader.readmessage()
            print(f"Received message\n {message}".replace("\r", "\n"))
            message_type = message.segment("MSH").extract_field(1, 9)
            response = create_response(
                message, message_type, ack_code, invalid_response)

            if timeout:
                print(f"Sleeping for {timeout} seconds")
                await asyncio.sleep(timeout)
                print(f"Responding with \n {response}".replace("\r", "\n"))
            elif skip_response:
                print("Skipping response")
            else:
                if empty_response:
                    print("response will be empty")
                    response = ""
                print(f"Responding with \n {response}".replace("\r", "\n"))
                hl7_writer.writemessage(response)
                await hl7_writer.drain()

    except asyncio.IncompleteReadError:
        if not hl7_writer.is_closing():
            hl7_writer.close()
            await hl7_writer.wait_closed()
    print(f"Connection closed {peername}")


async def server_loop(ack_code, timeout, skip_response, invalid_response, empty_response):
    print(f"Starting MLLP server on {PORT}")
    try:
        loop = partial(
            process_hl7_messages,
            ack_code=ack_code,
            timeout=timeout,
            skip_response=skip_response,
            invalid_response=invalid_response
        )

        async with await start_hl7_server(loop, port=PORT) as hl7_server:
            await hl7_server.serve_forever()
    except asyncio.CancelledError:
        print("Cancelled corutine")
    except Exception as e:
        print(f"Error occurred in main: {e}")


def create_response(message, message_type, ack_code, invalid_response):
    match message_type:
        case "QBP":
            return generate_k22(message, ack_code.value, invalid_response)
        case "ORU":
            return message.create_ack(ack_code.value)
        case _:
            raise RuntimeError(f"Unsupported message {message_type}")


def main(
    ack_code: ACKCode = ACKCode.AA,
    timeout_seconds: int = None,
    skip_response: bool = False,
    invalid_response: bool = False,
    empty_response: bool = False
):
    aiorun.run(
        server_loop(ack_code, timeout_seconds,
                    skip_response, invalid_response, empty_response),
        stop_on_unhandled_errors=True,
    )


if __name__ == "__main__":
    typer.run(main)
