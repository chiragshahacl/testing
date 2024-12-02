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
poetry install

# create .env file if needed
if ! test -f ".env"; then
  {
    echo "GITHUB_REPOSITORY=repository_name"
    echo "GITHUB_TOKEN=github_token"
  } >> .env
  echo "Local .env file created."
fi

echo "Checking code..."
if [[ -z "${CI}" ]]; then
  poetry run black .
  poetry run ruff check buildtools --fix
else
  poetry run black --check .
  poetry run ruff check buildtools
fi


# run tests
 poetry run pytest tests

