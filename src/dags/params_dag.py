from datetime import datetime, timedelta

from airflow import DAG
from airflow.models.param import Param

with DAG(
    dag_id="params_test",
    start_date=datetime(2023, 1, 1),
    schedule=timedelta(days=30),
    catchup=False,
    params={
        "x": Param(5, type="integer", minimum=3)
    }
) as dag:
    pass
