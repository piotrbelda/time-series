from datetime import datetime, timedelta
import json
import os
import re

import pandas as pd
from airflow import DAG
from airflow.decorators import task
from airflow.exceptions import AirflowSkipException
from airflow.operators.bash import BashOperator
from airflow.operators.python import PythonOperator
from airflow.sensors.filesystem import FileSensor
from airflow.hooks.base import BaseHook

import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent.parent.resolve()))

from app.taxi_parser import get_latest_taxi_data_url
from app.consts import cols_mapping
from app.db import Session

conn = BaseHook.get_connection("taxi_data")
FILE_NAME = "taxi_data.parquet"
FILE_DIR = json.loads(conn._extra)["path"]
FILE_PATH = os.path.join(FILE_DIR, FILE_NAME)


def get_latest_taxi_data_from_db():
    return "2023-10"


def parse_date_from_url(url):
    return re.search(r"\d{4}-\d{2}", url).group()


with DAG(
    dag_id="taxi_etl",
    start_date=datetime(2023, 1, 1),
    schedule=timedelta(days=30),
    catchup=False,
) as dag:

    @task(task_id="check")
    def checkout_latest_taxi_url():
        file_url = get_latest_taxi_data_url()
        new_data = parse_date_from_url(file_url)
        db_date = get_latest_taxi_data_from_db()
        if db_date == new_data:
            raise AirflowSkipException

        return file_url

    def transform():
        df = pd.read_parquet(FILE_PATH)
        df = df[list(cols_mapping.keys())]
        df = df.rename(columns=cols_mapping)
        assert df.columns.tolist() == list(cols_mapping.values())
        df.to_parquet(FILE_PATH)

    @task(task_id="load")
    def load(url: str):
        new_data = parse_date_from_url(url)
        year, month = (int(num) for num in new_data.split("-"))
        with Session() as session:
            session.bind.execute(
                f"""
                    CREATE TABLE IF NOT EXISTS trips_{year}_{month}
                    PARTITION OF trips
                    FOR VALUES FROM ('{year}-{month}-01') TO ('{year}-{month + 1}-01')
                """
            )
            df = pd.read_parquet(FILE_PATH)
            df = df[(df.tpep_pickup.dt.year == year) & (df.tpep_pickup.dt.month == month)]
            BATCH_SIZE = 10000
            for idx in range(0, len(df), BATCH_SIZE):
                chunk = df.iloc[idx: idx + BATCH_SIZE]
                chunk.to_sql("trips", con=session.bind, if_exists="append", index=False)
            session.commit()
        os.remove(FILE_PATH)

    file_check = FileSensor(
        task_id="file_check",
        fs_conn_id="taxi_data",
        filepath=FILE_NAME,
        poke_interval=1,
        timeout=3,
    )

    url = checkout_latest_taxi_url()
    extract_phase = BashOperator(
        task_id="extract",
        bash_command=f"wget -nc {url} -O {FILE_PATH}"
    )
    transform_phase = PythonOperator(
        task_id="transform",
        python_callable=transform,
    )
    load_phase = load(url)

    url >> extract_phase >> file_check >> transform_phase >> load_phase
