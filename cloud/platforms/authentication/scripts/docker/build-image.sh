#!/bin/bash

# builds local authentication service image
docker build -t authentication:local \
--build-arg APPLICATION_PORT=8000 \
-f Dockerfile ../../.
