#!/bin/bash

docker exec broker \
kafka-topics --bootstrap-server broker:9092 \
             --create \
             --topic auth-audit-trail-stream