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

# create .env file
./scripts/create_env.sh

# run formatters
if [[ -z "${CI}" ]]; then
  echo "Applying ruff fixes"
  poetry run ruff check . --select I --fix
  poetry run ruff format .

  echo "Applying Gherkin files formatting"
  poetry run reformat-gherkin features
else
  echo "Checking ruff formatting"
  poetry run ruff format .

  echo "Checking Gherkin files formatting"
  poetry run reformat-gherkin --check features
fi

# check pylint compliance
echo "Checking pylint compliance"
poetry run pylint --include-naming-hint=y src

# get unit and integration coverage and create report
echo "Running integrations tests and collecting coverage"
poetry run coverage run --source='./src' --concurrency thread,greenlet -m behave --format progress
poetry run coverage run -a --source='./src' --concurrency thread,greenlet -m pytest
poetry run coverage report --skip-covered --fail-under=70 -m
poetry run coverage html --directory reports
