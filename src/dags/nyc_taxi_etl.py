from datetime import datetime, timedelta
import json
import os

from airflow import DAG
from airflow.decorators import task
from airflow.exceptions import AirflowSkipException
from airflow.operators.bash import BashOperator
from airflow.sensors.filesystem import FileSensor
from airflow.hooks.base import BaseHook
import pandas as pd

import re

import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent.parent.resolve()))

from app.taxi_parser import get_latest_taxi_data_url

FILE_NAME = "taxi_data.parquet"
conn = BaseHook.get_connection("taxi_data")
FILE_DIR = json.loads(conn._extra)["path"]
FILE_PATH = os.path.join(FILE_DIR, FILE_NAME)


def get_latest_taxi_data_from_db():
    return "2023-10"


def parse_date_from_url(url):
    return re.search(r"\d{4}-\d{2}", url).group()


with DAG(
    dag_id="nyc_data",
    start_date=datetime(2023, 1, 1),
    schedule=timedelta(days=30),
    catchup=False,
) as dag:

    @task(task_id="check_new_data_availability")
    def checkout_taxi_url():
        file_url = get_latest_taxi_data_url()
        new_data = parse_date_from_url(file_url)
        db_date = get_latest_taxi_data_from_db()
        if db_date != new_data:
            raise AirflowSkipException
        
        return file_url

    @task(task_id="transform")
    def transform():
        df = pd.read_parquet(FILE_PATH)
        

    @task(task_id="load")
    def load():
        pass

    file_presence_check = FileSensor(
        task_id="is_taxi_data_available",
        fs_conn_id="taxi_data",
        filepath=FILE_NAME,
        poke_interval=1,
        timeout=3,
    )

    file_url = checkout_taxi_url()
    extract_phase = BashOperator(
        task_id="extract",
        bash_command=f"wget -nc {file_url} -O {FILE_PATH}"
    )
    transform_phase = transform()
    load_phase = load()

    file_url >> extract_phase >> file_presence_check >> transform_phase >> load_phase
