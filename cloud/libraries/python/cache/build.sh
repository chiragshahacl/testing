#!/usr/bin/env bash

# Exists on step failure
set -e

if [[ -z "$(which python3.11)" ]]; then
  echo "Could not find python 3.11 installed"
else
  echo "Using python3.11 for installation"
  poetry env use $(which python3.11)
fi

# install latest dependencies
echo "Installing dependencies"
poetry install

if ! test -f ".env"; then
  {
    echo "ENVIRONMENT=local"
    echo "REDIS_HOST=localhost"
    echo "REDIS_PORT=6379"
    echo "REDIS_USERNAME=user"
    echo "REDIS_PASSWORD=pass"
    echo "REDIS_CACHE_TTL=86400"
    echo "CACHE_ENABLED=True"
    echo "PROJECT_NAME=cache"
  } >> .env
  echo "Local .env file created."
fi

# run formatters
echo "Checking code..."
if [[ -z "${CI}" ]]; then
  poetry run ruff format .
else
  poetry run ruff check cache
fi

# get feature files coverage and create report
echo "Running integrations tests and collecting coverage"
poetry run coverage run --source='./cache' -m pytest tests
poetry run coverage html --directory reports
