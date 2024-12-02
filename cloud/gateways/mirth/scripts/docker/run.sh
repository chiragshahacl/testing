#!/bin/bash

# runs the container using local db
docker run --name="sibel-mirth" -d --network tucana -p 8443:8443 -p 8080:8080 -p 6661:6661 sibel-mirth:local
