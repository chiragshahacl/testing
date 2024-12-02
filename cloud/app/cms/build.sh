#!/usr/bin/env bash

# Exists on step failure
set -e

# Installing Packages
npm install

# Format and lint
echo '🎨💻🔨 Styling, testing and building your project!'
if [[ -z "${CI}" ]]; then
  echo "Formatting using Prettier"
  npm run format
fi

# Check Prettier standards
npm run check-format
if [ $? -ne 0 ]; then
  echo '❌❌❌ Prettier Check Failed. Run npm run format, add changes and try commit again.'
  exit 1
fi

echo '✅✅✅✅'
