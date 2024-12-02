#!/bin/bash

if test -z "$1"
then
  echo "Please provide a message for the migration"
  exit 0
fi
poetry run alembic revision --autogenerate -m "$1"
