#!/usr/bin/env bash

# Exists on step failure
set -e

echo "Checking project"
cargo check

./scripts/create_env.sh

# run formatters
if [[ -z "${CI}" ]]; then
    echo "Applying formatting"
    cargo clippy --fix --allow-dirty --allow-staged
else
    echo "Checking formatting"
    cargo clippy
fi


echo "Running tests"
cargo test

echo "Building project"
cargo build --release

echo "To execute the binary, run ./target/release/rkc"
