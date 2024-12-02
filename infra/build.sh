#!/usr/bin/env bash

# Exists on step failure
set -e

# run terraform format
terraform fmt --recursive .

# run tfsec
tfsec .
