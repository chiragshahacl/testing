#!/bin/bash

docker exec broker \
kafka-topics --bootstrap-server broker:9092 \
             --create \
             --topic patient-audit-trail-stream