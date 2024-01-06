FROM python:3.11.6-slim

RUN apt-get update && apt install -y vim

COPY ./requirements.txt /tmp

RUN pip install -r /tmp/requirements.txt

RUN mkdir app

WORKDIR /app

COPY ./app.py .
