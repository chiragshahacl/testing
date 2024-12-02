#!/usr/bin/env bash

## Colors
BLUE='\033[0;34m'
GREEN='\033[0;32m'
RED='\033[0;31m'
NC='\033[0m' # No Color

## Create env files
paths=(
    "./platforms/authentication/scripts/create_env.sh"
    "./platforms/audit_trail/scripts/create_env.sh"
    "./platforms/patient/scripts/create_env.sh"
    "./platforms/config/scripts/create_env.sh"
    "./platforms/emulator/scripts/create_env.sh"
    "./platforms/rkc/scripts/create_env.sh"
    "./gateways/realtime/scripts/create_env.sh"
    "./gateways/web/scripts/create_env.sh"
    "./gateways/sdc/scripts/create_properties.sh"
)

echo -e "${BLUE}Creating env files...${NC}"
for path in "${paths[@]}"
do
    "$path"
done

## Build the project
if [ "$1" = "--build" ]; then
    echo -e "${BLUE}Rebuilding project...${NC}"
    if [ -n "$2" ]; then
        docker compose build $2
    else
        docker compose build
    fi
    echo -e "${BLUE}Cleaning...${NC}"
    docker volume prune -f
    docker buildx prune -f
    docker image prune -f
fi

echo -e "${BLUE}Starting zookeper...${NC}"
docker compose up -d zookeeper
echo -e "${BLUE}Waiting for 5 seconds...${NC}"
sleep 5
echo -e "${BLUE}Starting the rest of the services...${NC}"
docker compose up -d

## kakfa topics
topics=(
    "vitals"
    "vitals-v2"
    "events-config"
    "events-patient"
    "events-device"
    "events-authentication"
    "events-sdc"
    "technical-alerts"
    "alerts"
    "sdc-realtime-state"
    "device-commands-requests"
    "healthcheck"
)

echo -e "${BLUE}Creating kafka topics...${NC}"
for topic in "${topics[@]}"
do
    output=$(docker exec broker kafka-topics --bootstrap-server broker:9092 --create --topic "$topic" 2>&1)

    if [[ $output == *"Topic '$topic' already exists"* ]]; then
        echo -e "Topic '$topic' already exists."
    else
        echo -e "${GREEN}Topic '$topic' created successfully.${NC}"
    fi
done

## Create databases
apps=(
    "authentication"
    "audit-trail"
    "patient"
    "config"
)

echo -e "${BLUE}Creating databases...${NC}"
for app in "${apps[@]}"
do
    output=$(docker exec -it "$app" python create_db.py 2>&1)

    if [[ $output == *"Attempting creation DB"* && $output == *"Database"* ]]; then
        echo -e "Database already exists in "$app" app, skipping."
    else
        echo "$output"
    fi
done

echo -e "${BLUE}Creating mirth database...${NC}"
output=$(docker exec -it "patient" python create_mirth_db.py 2>&1)

if [[ $output == *"Attempting creation DB"* && $output == *"Database"* ]]; then
    echo -e "Database already exists in "$app" app, skipping."
else
    echo "$output"
fi

## Run migrations
migrations_commands=(
    "docker exec -it authentication python manage.py migrate"
    "docker exec -it audit-trail python -m alembic upgrade head"
    "docker exec -it patient python -m alembic upgrade head"
    "docker exec -it config python -m alembic upgrade head"
)

echo -e "${BLUE}Running migrations...${NC}"
for app in "${apps[@]}"
do
    if [[ $app == "authentication" ]]; then
      output=$(docker exec -it "$app" python manage.py migrate 2>&1)
    else
      output=$(docker exec -it "$app" python -m alembic upgrade head 2>&1)
    fi

    if [[ $output == *"No migrations to apply."* ]]; then
        echo -e "No migrations to apply in "$app" app."
    elif [[ $output == *"Will assume transactional DDL"* ]]; then
        echo -e "Migration in "$app" app is up to date."
    else
        echo $output
    fi
done

## Create super user
output=$(docker exec -it authentication python manage.py create_system_user --email admin@sibelhealth.com --groups clinical --password pass --first_name admin --last_name admin 2>&1)
echo -e "${GREEN}$output ${NC}"


## Create tech user
output=$(docker exec -it authentication python manage.py create_system_user --email tech@sibelhealth.com --groups tech --password pass --first_name tech --last_name user 2>&1)
echo -e "${GREEN}$output ${NC}"


echo -e "${BLUE}Waiting for 10 seconds...${NC}"
docker compose up -d mirth
sleep 5

# Sync mirth config
output=$(docker exec -it mirth /opt/connect/mirthsync-3.1.0/bin/mirthsync.sh -i -s https://localhost:8443/mirth/api -d -u admin -p admin push -t /opt/connect/tucana_config 2>&1)
echo -e "${GREEN}$output ${NC}"

echo -e "${GREEN}Project is running... 🚀${NC}"
