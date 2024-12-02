#!/bin/bash

# builds local emulator container
docker build -t emulator:local \
--build-arg APPLICATION_PORT=8000 \
-f Dockerfile ../../.

