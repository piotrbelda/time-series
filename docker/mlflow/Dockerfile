FROM python:3.11.6-slim

ENV OWNER mlflow
RUN useradd -m ${OWNER}
USER ${OWNER}

ENV PATH="${PATH}:/home/${OWNER}/.local/bin"
WORKDIR /home/${OWNER}/mlflow

COPY --chown=${OWNER} requirements.txt /tmp
RUN pip install --user -r /tmp/requirements.txt

EXPOSE 8000

CMD mlflow server \
    --backend-store-uri ${MLFLOW_TRACKING_URI} \
    --default-artifact-root s3://${S3_BUCKET_NAME} \
    --host 0.0.0.0 \
    --port 8000
