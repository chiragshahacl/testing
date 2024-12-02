#!/bin/bash

# builds local auth container
docker build -t auth:local \
--build-arg APPLICATION_PORT=7006 \
-f Dockerfile ../../.
