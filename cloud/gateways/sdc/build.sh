#!/usr/bin/env bash

# Get the app path
properties_path=$(dirname $(dirname "$0"))/src/main/resources/config.properties

# Exists on step failure
set -e

# install latest dependencies
echo "Installing dependencies"
mvn install

if [[ -z "${CI}" ]]; then
  echo "Applying spotless fixes"
  mvn spotless:apply
fi

echo "Compiling"
mvn compile

if [ -e $properties_path ]
then
    # delete config.properties file
    ./scripts/delete_properties.sh
    echo "The existing configuration file is deleted."
fi
# create config.properties file
./scripts/create_properties.sh
