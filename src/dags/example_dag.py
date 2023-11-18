import time
from datetime import datetime, timedelta

import mlflow
from airflow import DAG
from airflow.decorators import task
from mlflow import MlflowClient

client = MlflowClient()


with DAG(
    dag_id="test_dag",
    start_date=datetime(2023, 11, 11),
    schedule=timedelta(days=1),
    catchup=False,
) as dag:
    
    @task(task_id="test-0")
    def test_0():
        print("starting run")
        run = mlflow.start_run()
        return {"run_id": run.info.run_id}


    @task(task_id="test-1")
    def test_1():
        print("sleeping 1")
        time.sleep(1)


    @task(task_id="test-2")
    def test_2():
        print("sleeping 2")
        time.sleep(1)


    @task(task_id="test-3")
    def test_3(d):
        print(f"run_id: {d['run_id']}")
        client.update_run(d["run_id"], status="FINISHED")


    t0 = test_0()
    t1 = test_1()
    t2 = test_2()
    t3 = test_3(t0)

    t0 >> t1 >> t2 >> t3
