#!/bin/bash

# runs the container locally
docker run --env-file=.env --name="emulator" -d -p 8002:8002 emulator:local

