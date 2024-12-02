#!/bin/bash

# builds local audit-trail container
docker build -t audit-trail:local \
--build-arg APPLICATION_PORT=8000 \
--build-arg REGISTRY_NAME=643361541825.dkr.ecr.us-east-2.amazonaws.com \
-f Dockerfile ../../.
