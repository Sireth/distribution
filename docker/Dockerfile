FROM ubuntu:24.04

RUN apt-get update && apt-get install -y \
    python3

RUN apt-get install -y pip

RUN mkdir /distribution

WORKDIR /distribution

COPY requirements.txt /distribution/requirements.txt

RUN pip install --upgrade pip && pip install -r requirements.txt

