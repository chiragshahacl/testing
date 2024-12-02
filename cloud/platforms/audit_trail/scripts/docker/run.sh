#!/bin/bash

# runs the container using local db
docker run --env-file=.env --name="audit-trail" -d -p 7003:7003 audit-trail:local

