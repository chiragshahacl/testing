#!/bin/bash

# runs the container locally
docker run --env-file=.env --name="realtime" -d -p 8000:8000 realtime:local

