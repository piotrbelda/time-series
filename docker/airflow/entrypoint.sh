#!/bin/bash

CONN_NAMES=(taxi_data postgres_db google_cloud_connection)
CONN_URIS=( \
    "path://:@:/?path=/opt/airflow/files" \
    "postgresql://${TAXI_DB_USER}:${TAXI_DB_PASSWORD}@${TAXI_DB_HOST}:${TAXI_DB_PORT}/${TAXI_DB_NAME}" \
    "google-cloud-platform://?key_path=${HOME}/keys/creds.json&scope=https%3A%2F%2Fwww.googleapis.com%2Fauth%2Fcloud-platform&project=${GCP_PROJECT_NAME}&num_retries=2" \
)

function initialize_airflow_services {
    # init metastore
    airflow db init
    # migrate metastore
    airflow db migrate
    # create admin user
    airflow users create -e "admin@airflow.com" -f "airflow" -l "airflow" -p "airflow" -r "Admin" -u "airflow"
    # run scheduler
    airflow scheduler &> /dev/null &
    # start Celery worker
    airflow celery worker &
}

function create_airflow_connections {
    IFS=" " read -ra names <<< "${1}"
    IFS=" " read -ra uris <<< "${2}"
    for idx in ${!names[@]}
    do
        airflow connections add ${names[idx]} --conn-uri ${uris[idx]}
    done
}

initialize_airflow_services
create_airflow_connections "${CONN_NAMES[*]}" "${CONN_URIS[*]}"

# run webserver
exec airflow webserver
