#!/usr/bin/env bash

# Exists on step failure
set -e

if [[ -z "$(which python3.11)" ]]; then
  echo "Could not find python 3.11 installed"
else
  echo "Using python3.11 for installation"
  poetry env use "$(which python3.11)"
fi

# install latest dependencies
echo "Installing dependencies"
poetry install

# run formatters
if [[ -z "${CI}" ]]; then
  echo "Applying ruff fixes"
  poetry run ruff check . --fix
  poetry run ruff format .
else
  echo "Checking ruff formatting"
  poetry run ruff check app
fi

# get feature files coverage and create report
echo "Running unit and integrations tests and collecting coverage"
#poetry run coverage run --source='./app' --concurrency thread -m pytest tests
#poetry run coverage run -a --source='./app' --concurrency thread -m behave --format progress
#poetry run coverage report --skip-covered
#poetry run coverage html --directory reports
