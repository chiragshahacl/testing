#!/usr/bin/env python3

import subprocess
import multiprocessing
import os
import signal
import time
import argparse
from os.path import isfile


JAR_PATH = "target/classes/Provider-1.0.0-SNAPSHOT.jar"


def run_provider_process(serial_number, address=None, verbose=False):
    try:
        jar_args = ["-sn", serial_number]
        if address:
            jar_args.extend(["-address", address])

        extra_args = {}
        if not verbose:
            extra_args["stdout"] = subprocess.DEVNULL

        print(f"Starting provider with S/N: {serial_number}")
        subprocess.run(
            ["java", "-jar", JAR_PATH, *jar_args],
            check=True,
            **extra_args
        )
    except subprocess.CalledProcessError as e:
        print(f"Error starting Provider with S/N: {serial_number}. Error: {e}")


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("n", help="Number of providers that will be started", type=int, default=1)
    parser.add_argument("--address", help="Local address used to connect to the correct ethernet interface", type=str)
    parser.add_argument(
        "--sn-prefix",
        help="Serial number prefix that will be used for the started Providers",
        type=str,
        default="1234",
    )
    parser.add_argument("--build", help="Force clean and build the Provider", action="store_true")
    parser.add_argument("--verbose", help="Show all the providers outputs", action="store_true")
    parser.add_argument("--flicker", help=(
            "Used to test connection and disconnection of devices. "
            "It starts and kills providers indefinitely to test memory leaks"
        ), action="store_true")
    args = parser.parse_args()

    if args.build or not isfile(JAR_PATH):
        subprocess.run(["mvn", "-DtargetClass=Provider", "clean", "package"])

    processes = []

    running = True
    while running:
        # Start background processes
        for i in range(args.n):
            serial_number = f"{args.sn_prefix}-0000-0000-{(i + 1):04}"
            process = multiprocessing.Process(target=run_provider_process, args=(serial_number, args.address, args.verbose))
            process.start()
            processes.append(process)

        # Wait for SIGTERM (Ctrl + C)
        if args.flicker:
            # Wait once and restart the devices
            try:
                time.sleep(20)
            except KeyboardInterrupt:
                running = False
        else:
            # Wait forever
            while running:
                try:
                    time.sleep(20)
                except KeyboardInterrupt:
                    running = False

        print("Terminating processes...")

        # Terminate all background processes
        for process in processes:
            process.terminate()

        # Wait for processes to finish
        for process in processes:
            process.join()

    print("All processes terminated.")


if __name__ == "__main__":
    main()
