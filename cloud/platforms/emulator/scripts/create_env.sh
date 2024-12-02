#!/usr/bin/env bash

# Get the app path
env_path=$(dirname $(dirname "$0"))/.env

# create .env file
{
  echo "DEBUG=True"
  echo "LOG_LEVEL=DEBUG"
  echo "GUNICORN_WORKERS=1"
  echo "ENVIRONMENT=local"
  echo "APPLICATION_PORT=7005"
  echo "BASE_PATH=/emulator"
  echo "TOTAL_MONITORS=64"
  echo "TOTAL_SENSORS_PER_MONITOR=4"
  echo "ECG_MAXIMUM_DATAPOINTS_PER_SECOND=256"
  echo "ECG_MESSAGE_INTERVAL_IN_SECONDS=0.5"
  echo "PLETH_MAXIMUM_DATAPOINTS_PER_SECOND=64"
  echo "PLETH_MESSAGE_INTERVAL_IN_SECONDS=0.5"
  echo "RR_MAXIMUM_DATAPOINTS_PER_SECOND=26"
  echo "RR_MESSAGE_INTERVAL_IN_SECONDS=0.5"
  echo "KAFKA_HOST=localhost"
  echo "KAFKA_PORT=9092"
  echo "KAFKA_PASSWORD=''"
  echo "KAFKA_CA_FILE_PATH=''"
  echo "KAFKA_CERT_FILE_PATH=''"
  echo "KAFKA_KEY_FILE_PATH=''"
  echo "KAFKA_VITALS_TOPIC=vitals"
  echo "KAFKA_ALERTS_TOPIC=alerts"
  echo "KAFKA_TECHNICAL_ALERTS_TOPIC=events-sdc"
  echo "KAFKA_DEVICE_TOPIC=events-sdc"
  echo "KAFKA_SDC_REALTIME_STATE_TOPIC=sdc-realtime-state"
  echo "CORS_ORIGINS=http://localhost:3000"
  echo "SIBEL_VERSION=local"
  echo "WEB_GATEWAY_URL=http://localhost:8000/web"
  echo "DEVICE_PLATFORM_URL=http://localhost:7002/device"
  echo "ADMIN_USERNAME=admin@sibelhealth.com"
  echo "ADMIN_PASSWORD=cantguessthis"
} > $env_path

echo "Local $env_path file created."
