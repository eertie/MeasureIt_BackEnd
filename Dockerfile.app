# For more information, please refer to https://aka.ms/vscode-docker-python
FROM python:3.11-slim

LABEL maintainer="Erik Dekker <erik@triple-q.nl>"

# Keeps Python from generating .pyc files in the container
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV PORT=8000
ENV PATH="/home/appuser/.local/bin:${PATH}"

RUN apt-get -y update && apt-get -y upgrade && python -m pip install --upgrade pip

WORKDIR /api
COPY requirements.txt /api
RUN python -m pip install -r requirements.txt
COPY ./api /api

RUN adduser -u 5678 --disabled-password --gecos "" appuser && chown -R appuser /api
USER appuser
EXPOSE $PORT

