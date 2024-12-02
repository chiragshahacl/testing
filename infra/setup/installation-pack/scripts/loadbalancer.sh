#!/bin/sh

set -o errexit
set -o nounset
IFS=$(printf '\n\t')

# Docker
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh
printf '\nDocker installed successfully\n\n'

printf 'Waiting for Docker to start...\n\n'
sleep 5

sudo docker compose version

# Startup
sudo docker compose --file haproxy/docker-compose.yaml down
sudo docker compose --file haproxy/docker-compose.yaml up -d