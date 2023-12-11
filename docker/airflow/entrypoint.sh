#!/bin/bash

# init metastore
airflow db init

# migrate metastore
airflow db migrate

# create admin user
airflow users create -e "admin@airflow.com" -f "airflow" -l "airflow" -p "airflow" -r "Admin" -u "airflow"

# run scheduler
airflow scheduler &> /dev/null &

# Celery worker
airflow celery worker &

# setup connection path for downloaded files
airflow connections add "taxi_data" --conn-uri "path://:@:/?path=/opt/airflow/dags/files"

# run webserver
exec airflow webserver
