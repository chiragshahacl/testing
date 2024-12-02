#!/bin/bash

# builds local realtime container
docker build -t realtime:local \
  --build-arg APPLICATION_PORT=7007 \
  -f Dockerfile ../../.

