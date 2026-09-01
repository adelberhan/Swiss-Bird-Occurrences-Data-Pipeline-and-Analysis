FROM python:3.12.11-slim


# from where dagster will start
WORKDIR /app/dagster_project

COPY requirements.txt /app/requirements.txt


RUN apt-get update \
    && apt-get install -y --no-install-recommends git \
    && rm -rf /var/lib/apt/lists/*
    
RUN pip install --no-cache-dir -r /app/requirements.txt


# Project root Dir
COPY . /app

ENV PYTHONPATH=/app
ENV DBT_PROFILES_DIR=/app/dbt-Swiss-Bird-Occurrences-Data-Pipeline-and-Analysis/bird_project_week2

EXPOSE 3000

CMD ["dagster", "dev", "-h", "0.0.0.0", "-p", "3000"]