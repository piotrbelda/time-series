from datetime import datetime, timedelta

from airflow import DAG
from airflow.decorators import task
from airflow.exceptions import AirflowSkipException
from airflow.sensors.filesystem import FileSensor

import re

import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent.parent.resolve()))

from taxi.taxi_parser import get_latest_taxi_data_url


def get_latest_taxi_data_from_db():
    return "2023-10"


def parse_date_from_url(url):
    return re.search(r"\d{4}-\d{2}", url).group()


with DAG(
    dag_id="nyc_data",
    start_date=datetime(2023, 11, 11),
    schedule=timedelta(days=1),
    catchup=False,
) as dag:

    @task(task_id="check_new_data_availability")
    def checkout_taxi_url():
        # return {"taxi_url": get_latest_taxi_data_url()}
        # return {"taxi_url": "https://d37ci6vzurychx.cloudfront.net/trip-data/yellow_tripdata_2023-10.parquet"}
        return "https://d37ci6vzurychx.cloudfront.net/trip-data/yellow_tripdata_2023-10.parquet"

    @task(task_id="extract")
    def extract(url):
        db_date = get_latest_taxi_data_from_db()
        new_data = parse_date_from_url(url)
        if db_date != new_data:
            raise AirflowSkipException

    @task(task_id="transform")
    def transform():
        pass

    @task(task_id="load")
    def load():
        pass

    file_presence_check = FileSensor(
        task_id="is_taxi_data_available",
        fs_conn_id="taxi_data",
        filepath="taxi_data.parquet",
        poke_interval=1,
        timeout=5,
    )

    file_url = checkout_taxi_url()
    extract_phase = extract(file_url)
    transform_phase = transform()
    load_phase = load()

    file_url >> extract_phase >> file_presence_check >> transform_phase >> load_phase
