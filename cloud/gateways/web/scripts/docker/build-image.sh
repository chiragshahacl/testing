#!/bin/bash

# builds local web container
docker build -t web:local \
--build-arg APPLICATION_PORT=8000 \
--build-arg REGISTRY_NAME=643361541825.dkr.ecr.us-east-2.amazonaws.com \
-f Dockerfile ../../.

