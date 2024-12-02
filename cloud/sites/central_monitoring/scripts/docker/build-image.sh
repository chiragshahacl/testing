#!/bin/bash

# builds local central-monitoring container
docker build -t central-monitoring:local -f Dockerfile ../../.
