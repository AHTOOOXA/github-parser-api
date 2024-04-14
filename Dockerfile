FROM python:3.12
LABEL authors="anton"

RUN mkdir /app

WORKDIR /app

COPY requirements.txt /app

RUN pip install -r requirements.txt

COPY . /app

# CMD gunicorn app.main:app --workers 1 --worker-class uvicorn.workers.UvicornWorker --bind=0.0.0.0:8000