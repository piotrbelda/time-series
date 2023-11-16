import mlflow

with mlflow.start_run():
    mlflow.log_param("test", 2)
