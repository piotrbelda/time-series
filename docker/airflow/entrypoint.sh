#!/bin/bash

# init metastore
airflow db init

# migrate metastore
airflow db migrate

# create admin user
airflow users create -e "admin@airflow.com" -f "airflow" -l "airflow" -p "airflow" -r "Admin" -u "airflow"

# run scheduler
airflow scheduler &> /dev/null &

# run webserver
exec airflow webserver
