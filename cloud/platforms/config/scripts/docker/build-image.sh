#!/bin/bash

# builds local config container
docker build -t config:local \
--build-arg APPLICATION_PORT=7005 \
-f Dockerfile ../../.
