from datetime import datetime, timedelta

from airflow import DAG
from airflow.decorators import task
from airflow.providers.google.cloud.operators.gcs import GCSCreateBucketOperator, GCSDeleteBucketOperator

with DAG(
    dag_id="taxi_etl_gcs",
    start_date=datetime(2023, 1, 1),
    schedule=timedelta(days=30),
    catchup=False,
):
    # create = GCSCreateBucketOperator(
    #     task_id="create_gcs_bucket",
    #     bucket_name="time_series_airflow_test_bucket",
    #     gcp_conn_id="google_cloud_connection",
    #     location="EU",
    #     storage_class="STANDARD",
    # )

    delete = GCSDeleteBucketOperator(
        task_id="delete_gcs_bucket",
        bucket_name="time_series_airflow_test_bucket",
        gcp_conn_id="google_cloud_connection",
    )
