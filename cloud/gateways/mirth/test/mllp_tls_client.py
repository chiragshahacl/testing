import random
import socket
import ssl

REMOTE_IP = "api.dev.tucana.sibel.health"
REMOTE_PORT = 6661
HEADER = bytes.fromhex("0b")
TRAILER = bytes.fromhex("1c0d")
SEGMENT_START = chr(11)  # Decimal value 11 represents VT
SEGMENT_TERMINATOR = "\r\n"
RANDOM_IDENTIFIER = {random.randint(999, 9999999)}

msg = f"{SEGMENT_START}\
MSH|^~\&|||||20170613103644||ADT^A04|MSG123|P|2.6{SEGMENT_TERMINATOR}\
EVN|A04|20170613103644|||{SEGMENT_TERMINATOR}\
PID|1||{RANDOM_IDENTIFIER}||Do^Joh^||19800101|M|||||555-123-4567^HOME^CP|||S|123456789|987654321|{SEGMENT_TERMINATOR}\
PV1|1|I|2000^2012^01||||004777^Doe^John^Jr^^^Dr.|004888^Smith^Jane^MD^^^Dr.|^|||S|||||||||||||||||||||||||20170613103644|{SEGMENT_TERMINATOR}\
"


def main():
    connect_to_server()


def connect_to_server():
    context = ssl.create_default_context()
    with context.wrap_socket(
        socket.socket(socket.AF_INET, socket.SOCK_STREAM), server_hostname=REMOTE_IP
    ) as sock:
        print(f"Connecting to server {REMOTE_IP} on port {REMOTE_PORT}")
        try:
            sock.connect((REMOTE_IP, REMOTE_PORT))
            print("Successfully connected to server")

            print("Sending message:")
            for x in msg.split(SEGMENT_TERMINATOR):
                print(x)

            sock.sendall(HEADER + bytearray(msg, "utf8") + TRAILER)
            print("Message sent.")
        except Exception as e:
            print(f"Connection failed. Reason: {e} \n")
            exit()

        # Get response from the server and print it
        while True:
            try:
                response = sock.recv(4096)
                response_str = response.decode("utf-8")
                response_str = response_str.replace(HEADER.decode(), "").replace(
                    TRAILER.decode(), ""
                )
                print("\nResponse received:")
                for x in response_str.split(SEGMENT_TERMINATOR):
                    print(x)
                break
            except Exception as e:
                print(f"Issue receiving response from the server. Reason: {e}")
                break

        print("Closing the connection.")
        sock.close()
        print("Connection closed.")


if __name__ == "__main__":
    main()
