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

# create .env file if needed
if ! test -f ".env"; then
  {
    echo "ENVIRONMENT=local"
  } >> .env
  echo "Local .env file created."
fi


# run formatters
if [[ -z "${CI}" ]]; then
  echo "Applying ruff fixes"
  poetry run ruff check . --select I --fix
  poetry run ruff format .

else
  echo "Checking ruff formatting"
  poetry run ruff check common_schemas
fi

# check pylint compliance
echo "Checking pylint compliance"
poetry run pylint --include-naming-hint=y common_schemas

# get feature files coverage and create report
echo "Running unit and integrations tests then collecting coverage"
poetry run coverage run -a --source='./common_schemas' -m pytest
poetry run coverage report --skip-covered --fail-under=90 -m
poetry run coverage html --directory reports
