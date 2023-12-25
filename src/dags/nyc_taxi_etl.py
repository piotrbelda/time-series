from datetime import datetime, timedelta
import json
import os
import re

import pandas as pd
from airflow import DAG
from airflow.decorators import task
from airflow.exceptions import AirflowSkipException
from airflow.operators.bash import BashOperator
from airflow.sensors.filesystem import FileSensor
from airflow.hooks.base import BaseHook
from airflow.providers.postgres.hooks.postgres import PostgresHook

import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent.parent.resolve()))

from app.taxi_parser import get_latest_taxi_data_url

FILE_NAME = "taxi_data.parquet"
conn = BaseHook.get_connection("taxi_data")
FILE_DIR = json.loads(conn._extra)["path"]
FILE_PATH = os.path.join(FILE_DIR, FILE_NAME)

cols_mapping = {
    "VendorID": "vendor_id",
    "tpep_pickup_datetime": "tpep_pickup",
    "tpep_dropoff_datetime": "tpep_dropoff",
    "passenger_count": "passenger_count",
    "trip_distance": "trip_distance",
    "RatecodeID": "rate_code_id",
    "store_and_fwd_flag": "store_and_fwd_flag",
    "PULocationID": "pu_location_id",
    "DOLocationID": "do_location_id",
    "payment_type": "payment_type",
    "fare_amount": "fare_amount",
    "extra": "extra",
    "tip_amount": "tip_amount",
    "total_amount": "total_amount",
}


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
        df = df[list(cols_mapping.keys())]
        df = df.rename(columns=cols_mapping)
        assert df.columns.tolist() == list(cols_mapping.values())
        df.to_parquet(FILE_PATH)

    @task(task_id="load")
    def load():
        df = pd.read_parquet(FILE_PATH)
        ph = PostgresHook(
            postgres_conn_id="postgres_db"
        )

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
