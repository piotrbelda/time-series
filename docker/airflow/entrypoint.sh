#!/bin/bash

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

# connections setup
airflow connections add "taxi_data" --conn-uri "path://:@:/?path=/opt/airflow/files"
airflow connections add "postgres_db" \
        --conn-uri "postgresql://${TAXI_DB_USER}:${TAXI_DB_PASSWORD}@${TAXI_DB_HOST}:${TAXI_DB_PORT}/${TAXI_DB_NAME}"
airflow connections add "google_cloud_connection" \
        --conn-uri "google-cloud-platform://?key_path=${HOME}/keys/creds.json&scope=https%3A%2F%2Fwww.googleapis.com%2Fauth%2Fcloud-platform&project=${GCP_PROJECT_NAME}&num_retries=2"

# run webserver
exec airflow webserver
