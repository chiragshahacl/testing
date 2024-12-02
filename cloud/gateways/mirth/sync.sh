#!/bin/bash

readonly retry_interval=10
readonly max_retries=5
readonly cookie_file=$(mktemp)
readonly request_header="X-Requested-With: syncScript"

echo "Sync process started..."
sleep 180

# Function to handle cleanup tasks
cleanup() {
  # Logout from the API
  curl -s -X POST "$ENDPOINT/users/_logout" -H "$reques_header" -b "$cookie_file" >/dev/null 2>&1

  # Clean up the session cookie file
  rm -f "$cookie_file"
}

# Trap the script exit to perform cleanup tasks
trap cleanup EXIT

# Wait for the server to become ready
retries=0
while true; do
  api_status=$(curl -s -o /dev/null -w "%{http_code}" --max-time 10 -X GET "$ENDPOINT/server/status" -H "$request_header" -k)
  if [ "$api_status" -eq 200 ]; then
    break
  else
    echo "Server is not ready. Status code $api_status, retrying in $retry_interval seconds"
    sleep "$retry_interval"
    retries=$((retries + 1))

    if [ "$retries" -ge "$max_retries" ]; then
      echo "Exceeded the maximum number of retries"
      exit 1
    fi
  fi
done

# Change the default password and store the session in a cookie file
api_status=$(curl -s -o /dev/null -w "%{http_code}" --max-time 10 -X POST "$ENDPOINT/users/_login" -H "$request_header" -d "username=$USER&password=admin" -L --location-trusted -k -c "$cookie_file")
if [ "$api_status" -eq 200 ]; then
  api_status=$(curl -s -o /dev/null -w "%{http_code}" --max-time 10 -X PUT "$ENDPOINT/users/1/password" -H "$request_header" -H "Content-Type: text/plain" -d "$PASS" -b "$cookie_file" -k)
  if [ "$api_status" -eq 204 ]; then
    echo "Password changed successfully"
  else
    echo "Failed to change password"
  fi
else
  api_status=$(curl -s -o /dev/null -w "%{http_code}" --max-time 10 -X POST "$ENDPOINT/users/_login" -H "$request_header" -d "username=$USER&password=$PASS" -L --location-trusted -k -c "$cookie_file")
  if [ "$api_status" -eq 200 ]; then
    echo "Successfully logged in"
  else
    echo "Failed to log in"
  fi
fi

if "${MIRTHSYNC_PATH}/mirthsync.sh" -i -s "$ENDPOINT" -d -u "$USER" -p "$PASS" push -t "$CONFIG_PATH"; then
  echo "Sync succeeded"
else
  echo "Failed to sync"
fi
