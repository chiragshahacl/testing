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

# Check ESLint Standards
npm run check-lint
if [ $? -ne 0 ]; then
  echo '❌❌❌ ESLint Check Failed. Make the required changes listed above, add changes and try to commit again.'
  exit 1
fi

# Run Tests
npm run unit-tests
if [ $? -ne 0 ]; then
  echo '❌❌❌ Tests failed: View the errors above to see why.'
  exit 1
fi

# Build storybook
npx playwright install && npm run build-storybook
if [ $? -ne 0 ]; then
  echo '❌❌❌ Storybook build failed: View the errors above to see why.'
fi

# Run storybook tests
npm run test-storybook
if [ $? -ne 0 ]; then
  echo '❌❌❌ Storybook tests failed: View the errors above to see why.'
  exit 1
fi


# Build app
npm run build
if [ $? -ne 0 ]; then
  echo '❌❌❌ Build failed: View the errors above to see why.'
  exit 1
fi

echo '✅✅✅✅'
