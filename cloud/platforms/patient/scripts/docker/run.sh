#!/bin/bash

# runs the container using local db
docker run --env-file=.env --name="patient" -d -p 7001:7001 --network tucana patient:local

