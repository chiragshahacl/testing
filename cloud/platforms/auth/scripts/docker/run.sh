#!/bin/bash

# runs the container using local db
docker run --env-file=.env --name="auth" -d -p 7006:7006 auth:local

