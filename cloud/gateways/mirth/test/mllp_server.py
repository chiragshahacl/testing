import asyncio

from hl7.mllp import start_hl7_server


async def process_hl7_messages(hl7_reader, hl7_writer):
    """This will be called every time a socket connects
    with us.
    """
    peername = hl7_writer.get_extra_info("peername")
    print(f"Connection established {peername}")
    try:
        # We're going to keep listening until the writer
        # is closed. Only writers have closed status.
        while not hl7_writer.is_closing():
            hl7_message = await hl7_reader.readmessage()
            print(f"Received message\n {hl7_message}".replace("\r", "\n"))
            # Now let's send the ACK and wait for the
            # writer to drain
            hl7_writer.writemessage(hl7_message.create_ack())
            await hl7_writer.drain()
    except asyncio.IncompleteReadError:
        # Oops, something went wrong, if the writer is not
        # closed or closing, close it.
        if not hl7_writer.is_closing():
            hl7_writer.close()
            await hl7_writer.wait_closed()
    print(f"Connection closed {peername}")


async def main():
    try:
        async with await start_hl7_server(
            process_hl7_messages, port=6661
        ) as hl7_server:
            await hl7_server.serve_forever()
    except asyncio.CancelledError:
        pass
    except Exception:
        print("Error occurred in main")


asyncio.run(main(), debug=True)
