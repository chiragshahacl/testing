#!/usr/bin/env bash

# Get the app path
properties_path=$(dirname $(dirname "$0"))/src/main/resources/config.properties

rm -- $properties_path