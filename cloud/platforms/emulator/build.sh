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
  poetry run ruff check src

  echo "Checking Gherkin files formatting"
  poetry run reformat-gherkin --check features
fi

# check pylint compliance
echo "Checking pylint compliance"
# TODO: remove the "-d duplicate-code" flag once the old emulation module get removed
poetry run pylint -d duplicate-code --include-naming-hint=y src

# get feature files coverage and create report
echo "Running integrations tests and collecting coverage"
poetry run coverage run --source='./src' -m behave --format progress
poetry run coverage run -a --source='./src' -m pytest tests
poetry run coverage html --directory reports
