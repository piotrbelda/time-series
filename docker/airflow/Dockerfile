FROM python:3.11.6-slim

ARG AIRFLOW_VERSION=2.8.0
ARG AIRFLOW_HOME=/opt/airflow
ARG OWNER=airflow

ENV AIRFLOW_HOME=${AIRFLOW_HOME}
ENV AIRFLOW__CORE__LOAD_EXAMPLES=False

RUN apt-get update && apt-get install -y vim wget
RUN pip install -U pip && \
    pip install apache-airflow[postgres,celery]==${AIRFLOW_VERSION} \
    --constraint https://raw.githubusercontent.com/apache/airflow/constraints-${AIRFLOW_VERSION}/constraints-3.11.txt && \
    pip install apache-airflow-providers-redis==3.4.1 && \
    pip install apache-airflow-providers-google==10.12.0

COPY ./requirements.txt /tmp
RUN pip install -r /tmp/requirements.txt

RUN useradd -m -d ${AIRFLOW_HOME} ${OWNER}
WORKDIR ${AIRFLOW_HOME}

COPY --chown=${OWNER} ./entrypoint.sh .
RUN chmod +x entrypoint.sh

RUN chown -R ${OWNER} ${AIRFLOW_HOME}
USER ${OWNER}

RUN mkdir dags

EXPOSE 8080

CMD ./entrypoint.sh
