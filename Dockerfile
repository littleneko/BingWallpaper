# syntax=docker/dockerfile:1

FROM python:3.10-slim

WORKDIR /bing

COPY requirements.txt requirements.txt
RUN pip3 install -r requirements.txt
COPY src/ .
COPY entrypoint.sh .
RUN chmod +x entrypoint.sh

RUN apt-get update && apt-get install -y \
    gosu \
    && rm -rf /var/lib/apt/lists/*

ENTRYPOINT ["/bing/entrypoint.sh", "python3", "app.py", "--service-mode"]
