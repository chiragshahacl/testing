#!/usr/bin/env bash

# Get the app path
env_path=$(dirname $(dirname "$0"))/.env

# create .env file
{
    echo 'RUST_INFO=info'
    echo "KAFKA_SERVER=localhost:9092"
    echo "KAFKA_TOPICS=vitals"
    echo "KAFKA_GROUP=vitals"
    echo 'KAFKA_PASSWORD=""'
    echo 'KAFKA_CA_FILE_PATH=""'
    echo 'KAFKA_CERT_FILE_PATH=""'
    echo 'KAFKA_KEY_FILE_PATH=""'
    echo "ENVIRONMENT=local"
    echo 'SENTRY_DSN=""'
    echo 'SIBEL_VERSION="0.1"'
    echo "VITALS_EXPORT_ENABLED=True"
    echo "VITALS_FLUSH_ENDPOINT=http://localhost:6662/consume/"
    echo "VITALS_FLUSH_TIMEOUT_SECONDS=10"
} > $env_path

echo "Local $env_path file created."
