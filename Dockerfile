FROM python:3.12.11-slim


# from where dagster will start
WORKDIR /app/dagster_project

COPY requirements.txt /app/requirements.txt


RUN sed -i 's|http://deb.debian.org|https://deb.debian.org|g' /etc/apt/sources.list.d/debian.sources \
    && apt-get update \
    && apt-get install -y --no-install-recommends git \
    && rm -rf /var/lib/apt/lists/*
    
RUN pip install --no-cache-dir -r /app/requirements.txt


# Project root Dir
COPY . /app

ENV PYTHONPATH=/app
ENV DBT_PROFILES_DIR=/app/dbt-Swiss-Bird-Pipeline/dbt_project

EXPOSE 3000

CMD ["dagster", "dev", "-h", "0.0.0.0", "-p", "3000"]