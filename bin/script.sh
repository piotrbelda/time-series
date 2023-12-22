#!/bin/bash

if [[ $# -eq 0 ]]
then
    ARGS=bash
else
    ARGS=$@
fi

docker compose exec -it airflow $ARGS
