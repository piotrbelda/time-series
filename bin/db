#!/bin/bash

if [[ $# -eq 0 ]]
then
    DB_NAME=taxi
elif [[ $# -gt 1 ]]
then
    echo "You need to pass database single name only!"
    exit 1
else
    DB_NAME="$@"
fi

docker compose exec -it db psql -U postgres -d $DB_NAME
