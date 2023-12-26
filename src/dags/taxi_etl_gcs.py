import time
from datetime import datetime, timedelta

from airflow import DAG
from airflow.providers.google.cloud.operators.gcs import GCSCreateBucketOperator, GCSDeleteBucketOperator
from airflow.providers.google.cloud.transfers.local_to_gcs import LocalFilesystemToGCSOperator
from airflow.operators.python import PythonOperator


def sleep_():
    time.sleep(30)


with DAG(
    dag_id="taxi_etl_gcs",
    start_date=datetime(2023, 1, 1),
    schedule=timedelta(days=30),
    catchup=False,
):
    create = GCSCreateBucketOperator(
        task_id="create_gcs_bucket",
        bucket_name="time_series_airflow_test_bucket",
        gcp_conn_id="google_cloud_connection",
        location="EU",
        storage_class="STANDARD",
    )

    upload = LocalFilesystemToGCSOperator(
        task_id="upload_taxi_data",
        src="/opt/airflow/files/test.parquet",
        dst="test.parquet",
        bucket="time_series_airflow_test_bucket",
        gcp_conn_id="google_cloud_connection",
    )

    sleep = PythonOperator(
        task_id="sleep_30",
        python_callable=sleep_,
    )

    delete = GCSDeleteBucketOperator(
        task_id="delete_gcs_bucket",
        bucket_name="time_series_airflow_test_bucket",
        gcp_conn_id="google_cloud_connection",
    )

    create >> upload >> sleep >> delete
