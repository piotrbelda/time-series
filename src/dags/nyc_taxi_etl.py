from datetime import datetime, timedelta

from airflow import DAG
from airflow.decorators import task
from airflow.sensors.filesystem import FileSensor

with DAG(
    dag_id="nyc_data",
    start_date=datetime(2023, 11, 11),
    schedule=timedelta(days=1),
    catchup=False,
) as dag:

    @task(task_id="extract")
    def extract():
        pass

    @task(task_id="transform")
    def transform():
        pass

    @task(task_id="load")
    def load():
        pass

    t1_5 = FileSensor(
        task_id="is_taxi_data_available",
        fs_conn_id="taxi_data",
        filepath="dupa.csv",
        poke_interval=1,
        timeout=5,
    )

    t1 = extract()
    t2 = transform()
    t3 = load()

    t1 >> t1_5 >> t2 >> t3
