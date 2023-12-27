from datetime import datetime, timedelta

import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent.parent.resolve()))

from airflow import DAG
from airflow.providers.google.cloud.transfers.gcs_to_bigquery import GCSToBigQueryOperator
from airflow.providers.google.cloud.operators.bigquery import BigQueryCreateEmptyDatasetOperator, BigQueryCreateEmptyTableOperator

from app.env import GCP_PROJECT_NAME

with DAG(
    dag_id="taxi_etl_gcs_to_bq",
    start_date=datetime(2023, 1, 1),
    schedule=timedelta(days=30),
    catchup=False,
) as dag:
    dataset = BigQueryCreateEmptyDatasetOperator(
        task_id="create_dataset",
        gcp_conn_id="google_cloud_connection",
        project_id=GCP_PROJECT_NAME,
        dataset_id="taxi",
        location="EU",
    )

    table = BigQueryCreateEmptyTableOperator(
        task_id="create_table",
        dataset_id=dataset.dataset_id,
        table_id="trips",
        project_id=GCP_PROJECT_NAME,
        gcp_conn_id="google_cloud_connection",
    )

    gcs_to_bq = GCSToBigQueryOperator(
        task_id="transfer",
        bucket="time_series_airflow_test_bucket",
        gcp_conn_id="google_cloud_connection",
        destination_project_dataset_table=f"{dataset.dataset_id}.{table.table_id}",
        project_id=GCP_PROJECT_NAME,
        source_objects="test.parquet",
        source_format="PARQUET",
        write_disposition="WRITE_TRUNCATE",
    )

    dataset >> table >> gcs_to_bq
