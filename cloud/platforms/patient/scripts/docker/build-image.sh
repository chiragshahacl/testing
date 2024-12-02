#!/bin/bash

# builds local patient container
docker build -t patient:local \
--build-arg APPLICATION_PORT=7001 \
--build-arg REGISTRY_NAME=643361541825.dkr.ecr.us-east-2.amazonaws.com \
-f Dockerfile ../../.
