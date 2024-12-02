#!/bin/bash

# runs the container using local db
docker run --env-file=.env --name="config" -d -p 7005:7005 config:local

