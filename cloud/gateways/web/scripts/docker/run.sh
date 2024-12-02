#!/bin/bash

# runs the container locally
docker run --env-file=.env --name="web" -d -p 8000:8000 web:local

