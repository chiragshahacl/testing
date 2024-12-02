#!/bin/bash

# runs the container
docker run --name="central-monitoring" -d -p 3000:3000 --network tucana central-monitoring:local

