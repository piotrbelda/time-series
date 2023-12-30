import json
import os
import re
from datetime import date, datetime, timedelta
from dateutil.relativedelta import relativedelta

import pandas as pd
from airflow import DAG
from airflow.decorators import task
from airflow.exceptions import AirflowSkipException
from airflow.operators.bash import BashOperator
from airflow.operators.python import PythonOperator
from airflow.sensors.filesystem import FileSensor
from airflow.hooks.base import BaseHook
from airflow.models.param import Param

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


def get_latest_taxi_data_from_db() -> str:
    with Session() as session:
        results = session.bind.execute(
            """
                SELECT
                    (regexp_matches(t.table_name, '\d{4}_\d{2}$'))[1]
                FROM information_schema.tables t
                WHERE t.table_schema='public'
                AND t.table_name LIKE 'trips_%%';
            """
        ).fetchall()
    if not results:
        return None

    dates = [date[0].split("_") for date in results]
    dates = [[int(num) for num in date] for date in dates]
    dates = sorted(dates, key=lambda array: (array[0], array[1]), reverse=True)
    last_date = dates[0]
    print(last_date)
    return "-".join(str(num) for num in last_date)


def parse_date_from_url(url):
    return re.search(r"\d{4}-\d{2}", url).group()


with DAG(
    dag_id="taxi_etl",
    start_date=datetime(2023, 1, 1),
    schedule=timedelta(days=30),
    catchup=False,
    params={
        "date": Param("2023-10-01", type="string", format="date"),
    },
) as dag:

    @task(task_id="check")
    def checkout_latest_taxi_url():
        file_url = get_latest_taxi_data_url()
        new_data = parse_date_from_url(file_url)
        db_date = get_latest_taxi_data_from_db()
        if db_date and db_date == new_data:
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
        dt = date(year, month, 1) + relativedelta(months=1)
        with Session() as session:
            session.bind.execute(
                f"""
                    CREATE TABLE IF NOT EXISTS trips_{year}_{month}
                    PARTITION OF trips
                    FOR VALUES FROM ('{year}-{month}-01') TO ('{dt.year}-{dt.month + 1}-01')
                """
            )
            df = pd.read_parquet(FILE_PATH)
            df = df[(df.tpep_pickup.dt.year == year) & (df.tpep_pickup.dt.month == month)]
            BATCH_SIZE = 10000
            for idx in range(0, len(df), BATCH_SIZE):
                df_chunk = df.iloc[idx: idx + BATCH_SIZE]
                df_chunk.to_sql("trips", con=session.bind, if_exists="append", index=False)
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
