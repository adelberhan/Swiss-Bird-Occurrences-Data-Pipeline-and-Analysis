# Swiss Bird Occurrences Data Platform

[![CI](https://github.com/adelberhan/WildData/actions/workflows/ci.yml/badge.svg)](https://github.com/adelberhan/WildData/actions/workflows/ci.yml)

## Overview

The **Swiss Bird Occurrences Data Platform** is an end-to-end data engineering pipeline designed to ingest, process, model, and serve wild bird observation data in Switzerland.

The platform processes records from the **Global Biodiversity Information Facility (GBIF)** REST API (class _Aves_, country code `CH`), ingests raw events via **dlt**, stores and models them in **Snowflake** across Curated and Serving data marts using **dbt**, and orchestrates the entire lifecycle with **Dagster** deployed via **Docker Compose**.

### Key Outcomes

- **Raw Data Ingestion**: Automated extraction of up to 1,000 occurrence records per run with nested JSON media URL extraction and issue normalization.
- **Dimensional Modeling**: Snowflake star-schema consisting of a deduplicated species dimension (`dim_species`), dataset dimension (`dim_dataset`), and an occurrence fact table (`fct_occurrences`).
- **Analytical Marts**: Pre-aggregated data marts serving species occurrence summaries, annual observation trends, and data quality issue metrics.
- **Automated Scheduling**: Daily scheduled materialization (`0 2 * * *`) via Dagster daemon.

---

## Architecture

The diagram below illustrates the end-to-end data flow and containerized service architecture:

```mermaid
flowchart TD
    subgraph EXT[External Source]
        GBIF[GBIF Occurrence Search REST API\ncountry: CH | classKey: 212]
    end

    subgraph DOCKER[Docker Compose Environment]
        subgraph DAGSTER_ENV[Dagster Orchestration]
            DAGSTER_WEB[webserver\nport: 3000]
            DAGSTER_DAEMON[daemon\nschedule runner]
            DAGSTER_CODE[code_location\ngRPC port: 4000]
            DAGSTER_PG[(postgres:16\nDagster Storage: 5432)]
        end
        DAGSTER_PG --- DAGSTER_CODE
        DAGSTER_PG --- DAGSTER_WEB
        DAGSTER_PG --- DAGSTER_DAEMON
        DAGSTER_WEB --- DAGSTER_CODE
        DAGSTER_DAEMON --- DAGSTER_CODE
    end

    subgraph SNOWFLAKE[Snowflake Data Warehouse: BIRD_DATA_DB]
        subgraph RAW_LAYER[Schema: RAW_DATA]
            OCC_RAW[(OCCURRENCES_RAW)]
            OCC_ISSUES[(OCCURRENCES_RAW__ISSUES)]
        end

        subgraph CURATED_LAYER[Schema: CURATED]
            STG[stg_occurrences\nview]
            DIM_SPEC[dim_species\ntable]
            DIM_DSET[dim_dataset\ntable]
            FCT_OCC[fct_occurrences\ntable]
        end

        subgraph SERVING_LAYER[Schema: SERVING]
            SUMM[species_occurrence_summary\ntable]
            YEAR[occurrences_by_year\ntable]
            QUAL[data_quality_summary\ntable]
        end
    end

    GBIF -->|dlt extract & load| OCC_RAW
    GBIF -->|dlt normalized list| OCC_ISSUES
    OCC_RAW --> STG
    OCC_ISSUES -. dlt parent ID join .-> FCT_OCC
    STG --> DIM_SPEC
    STG --> DIM_DSET
    STG --> FCT_OCC
    DIM_SPEC -. foreign key .-> FCT_OCC
    DIM_DSET -. foreign key .-> FCT_OCC
    FCT_OCC --> SUMM
    FCT_OCC --> YEAR
    FCT_OCC --> QUAL

    DAGSTER_CODE -->|Trigger gbif_dlt_asset| GBIF
    DAGSTER_CODE -->|Trigger swiss_bird_dbt_assets / dbt build| CURATED_LAYER
    DAGSTER_CODE -->|dbt build| SERVING_LAYER
```

---

## Repository Structure

```text
.
├── .dlt/                           # Local DLT configuration and secrets
├── .github/workflows/ci.yml        # CI pipeline (Ruff lint, dbt parse, Dagster check)
├── dagster_project/                # Dagster orchestration package & code location
│   ├── dagster_project/
│   │   ├── assets.py               # DLT ingestion asset (gbif_dlt_asset)
│   │   ├── dbt_assets.py           # dbt assets, translator, DbtCliResource
│   │   └── definitions.py          # Asset jobs, schedules (bird_daily_schedule)
│   ├── pyproject.toml              # Dagster package configuration
│   └── README.md                   # Dagster component documentation
├── dbt-Swiss-Bird-Pipeline/        # dbt transformation layer
│   ├── dbt_project/                # Active dbt project
│   │   ├── macros/                 # Custom schema generation macro
│   │   ├── models/                 # Curated (staging, dims, facts) & Serving models
│   │   ├── dbt_project.yml         # dbt project configuration
│   │   ├── profiles.yml            # Snowflake connection profiles
│   │   └── README.md               # dbt component documentation
│   └── README.md                   # dbt directory overview
├── dlt_project/                   # dlt ingestion engine
│   ├── config.py                   # GBIF field definitions (KEEP_FIELDS)
│   ├── pipeline.py                 # dlt source, Snowflake destination & loader
│   └── README.md                   # dlt component documentation
├── data/                           # Local CSV / raw JSON exports from prototype
├── app.py                          # Standalone initial ETL prototype script
├── dagster.yaml                    # Dagster instance storage config (Postgres backend)
├── docker-compose.yml              # Multi-container service definitions
├── Dockerfile                      # Python 3.12 container image for Dagster services
├── requirements.txt                # Root Python dependencies
├── workspace.yaml                  # Dagster workspace mapping to code_location gRPC
├── .emv.example                    # Environment variable template
└── Readme.md                       # Project root documentation
```

---

## Components

| Component          | Purpose                                                                                 | Technology                                            | Documentation                                                                               |
| :----------------- | :-------------------------------------------------------------------------------------- | :---------------------------------------------------- | :------------------------------------------------------------------------------------------ |
| **Ingestion**      | Extracts GBIF bird occurrences, normalizes payloads, and loads to Snowflake             | [dlt (data load tool)](https://dlthub.com/)           | [dlt_project/README.md](./dlt_project/README.md)                                            |
| **Transformation** | Cleans, deduplicates, dimensions, and serves analytical marts in Snowflake              | [dbt-core](https://www.getdbt.com/) & `dbt-snowflake` | [dbt-Swiss-Bird-Pipeline/README.md](./dbt-Swiss-Bird-Pipeline/dbt_project/README.md) |
| **Orchestration**  | Schedules pipeline runs, coordinates asset materializations, and tracks lineage         | [Dagster](https://dagster.io/) (`dagster-dbt`)        | [dagster_project/README.md](./dagster_project/README.md)                                    |
| **Infrastructure** | Containerizes PostgreSQL metadata storage, Dagster webserver, daemon, and code location | [Docker](https://www.docker.com/) & Docker Compose    | See [Docker Setup](#method-1-running-via-docker-compose-recommended) below                  |
| **Warehouse**      | Cloud analytical storage holding `RAW_DATA`, `CURATED`, and `SERVING` schemas           | [Snowflake](https://www.snowflake.com/)               | Managed via dbt profiles & dlt destination                                                  |

---

## End-to-End Data Flow

1. **Extraction (GBIF API)**:
   - DLT issues paginated HTTP GET requests to `https://api.gbif.org/v1/occurrence/search` filtering on Switzerland (`country=CH`), observations between 2015 and 2026 (`year=2015,2026`), and birds (`classKey=212`).
   - Limits extraction up to 1,000 records in batches of 300.
   - Extracts nested image URLs from the `media` array as `media_url`.
2. **Raw Storage (Snowflake `RAW_DATA`)**:
   - DLT writes records to `BIRD_DATA_DB.RAW_DATA.OCCURRENCES_RAW` with `write_disposition="replace"`.
   - DLT automatically unrolls the nested `issues` array into child table `OCCURRENCES_RAW__ISSUES` linked by `_DLT_PARENT_ID`.
3. **Orchestration Hand-off (Dagster)**:
   - The asset `gbif_dlt_asset` completes and Dagster automatically transitions to downstream dbt models using `CustomDagsterDbtTranslator`, which maps `source('raw_data', 'OCCURRENCES_RAW')` to `gbif_dlt_asset`.
4. **Staging & Curation (dbt `CURATED`)**:
   - `stg_occurrences` (view) renames columns to `snake_case`, casts data types, and exposes `_DLT_ID AS dlt_id`.
   - `dim_species` (table) deduplicates species by `species_key` using a window function favoring `ACCEPTED` taxonomic status.
   - `dim_dataset` (table) aggregates observation metrics per `dataset_key`.
   - `fct_occurrences` (table) aggregates issue flags from `OCCURRENCES_RAW__ISSUES` by parent ID into an array and left-joins onto staging occurrences.
5. **Serving Layer (dbt `SERVING`)**:
   - `species_occurrence_summary`: Occurrence counts, date spans, and coordinate coverage per species.
   - `occurrences_by_year`: Species observation counts broken down by year.
   - `data_quality_summary`: Issue flag distribution across all occurrences using Snowflake's `LATERAL FLATTEN`.

---

## Setup & Prerequisites

### Prerequisites

- **Python**: Version **3.12**
- **Docker & Docker Compose**: Docker Desktop or Docker Engine v24+ with Compose v2+
- **Snowflake Account**: With permissions to create/access:
  - Database: `BIRD_DATA_DB`
  - Warehouse: `COMPUTE_WH`
  - Role: `BIRD_DEV_ROLE`

### Environment Variables Configuration

Copy `.emv.example` to `.env` in the repository root:

```bash
cp .emv.example .env
```

Populate `.env` with your Snowflake credentials (both `SNOWFLAKE_*` and `DESTINATION__SNOWFLAKE__*` keys are required for dbt and DLT respectively):

```env
# dbt Snowflake Connection
SNOWFLAKE_ACCOUNT=<your_account_locator>
SNOWFLAKE_DATABASE=BIRD_DATA_DB
SNOWFLAKE_USER=<your_username>
SNOWFLAKE_PASSWORD=<your_password>
SNOWFLAKE_WAREHOUSE=COMPUTE_WH
SNOWFLAKE_ROLE=BIRD_DEV_ROLE
SNOWFLAKE_SCHEMA=RAW_DATA

# dlt Snowflake Destination Credentials
DESTINATION__SNOWFLAKE__CREDENTIALS__HOST=<your_account_locator>.snowflakecomputing.com
DESTINATION__SNOWFLAKE__CREDENTIALS__DATABASE=BIRD_DATA_DB
DESTINATION__SNOWFLAKE__CREDENTIALS__USERNAME=<your_username>
DESTINATION__SNOWFLAKE__CREDENTIALS__PASSWORD=<your_password>
DESTINATION__SNOWFLAKE__CREDENTIALS__WAREHOUSE=COMPUTE_WH
DESTINATION__SNOWFLAKE__CREDENTIALS__ROLE=BIRD_DEV_ROLE
```

---

## Running the Complete Pipeline

### Method 1: Running via Docker Compose (Recommended)

Docker runs the complete stack with an isolated PostgreSQL metadata database, Dagster code location server, daemon, and UI webserver.

```bash
# 1. Clone the repository
git clone https://github.com/adelberhan/WildData.git
cd WildData

# 2. Configure environment
cp .emv.example .env
# Edit .env with your credentials

# 3. Build and launch all services in the background
docker compose up --build -d

# 4. Check service status
docker compose ps

# 5. Follow runtime logs
docker compose logs -f
```

#### Accessing the Dagster UI

Open [http://localhost:3000](http://localhost:3000) in your browser:

1. Navigate to **Deployment** $\rightarrow$ **Assets**.
2. Click **Materialize all** in the top right to execute the complete end-to-end pipeline (`bird_pipeline_job`).
3. To enable the daily schedule (02:00 UTC), go to **Automation** $\rightarrow$ **Schedules** and switch on `bird_daily_schedule`.

#### Stopping the Stack

```bash
docker compose down
```

---

### Method 2: Running Locally (CLI / Python Virtual Environment)

If you prefer to run the components directly on your host machine:

#### 1. Setup Virtual Environment

```bash
python -m venv .venv

# On Windows
.\.venv\Scripts\Activate.ps1

# On Linux/macOS
source .venv/bin/activate

pip install -r requirements.txt
```

#### 2. Run Ingestion (DLT)

```bash
# Set Python path to project root
$env:PYTHONPATH = "."        # PowerShell
# export PYTHONPATH="."      # Linux/macOS

python -m dlt_project.pipeline
```

#### 3. Run Transformations (dbt)

```bash
$env:DBT_PROFILES_DIR = "$pwd\dbt-Swiss-Bird-Pipeline\dbt_project"

# Parse and compile manifest
dbt parse --project-dir .\dbt-Swiss-Bird-Pipeline\dbt_project

# Build models and run schema tests
dbt build --project-dir .\dbt-Swiss-Bird-Pipeline\dbt_project
```

#### 4. Launch Dagster Dev Server

```bash
$env:DAGSTER_HOME = "$pwd\dagster_project"
$env:PYTHONPATH = "."

dagster dev -m dagster_project.definitions -h 0.0.0.0 -p 3000
```

Open [http://localhost:3000](http://localhost:3000) to view and trigger the orchestrated assets.

---

## Verifying Successful Execution

1. **In Dagster UI** ([http://localhost:3000](http://localhost:3000)):
   - Under **Runs**, inspect the latest execution of `bird_pipeline_job`.
   - Ensure `gbif_dlt_asset` status is green (SUCCESS) with event logs showing 1,000 records loaded.
   - Ensure all dbt model assets (`stg_occurrences`, `dim_species`, `dim_dataset`, `fct_occurrences`, `species_occurrence_summary`, `occurrences_by_year`, `data_quality_summary`) and tests are green.
2. **In Snowflake**:
   Run the following query in your Snowflake worksheet:

   ```sql
   USE ROLE BIRD_DEV_ROLE;
   USE WAREHOUSE COMPUTE_WH;
   USE DATABASE BIRD_DATA_DB;

   -- Check raw landing
   SELECT COUNT(*) FROM RAW_DATA.OCCURRENCES_RAW;        -- 1000 records
   SELECT COUNT(*) FROM RAW_DATA.OCCURRENCES_RAW__ISSUES; -- Normalized issue flags

   -- Check curated models
   SELECT COUNT(*) FROM CURATED.DIM_SPECIES;
   SELECT COUNT(*) FROM CURATED.FCT_OCCURRENCES;

   -- Check analytical serving marts
   SELECT * FROM SERVING.SPECIES_OCCURRENCE_SUMMARY ORDER BY OCCURRENCE_COUNT DESC LIMIT 10;
   SELECT * FROM SERVING.DATA_QUALITY_SUMMARY ORDER BY RECORD_COUNT DESC;
   ```

---

## Continuous Integration (CI)

The repository includes GitHub Actions CI checks (`.github/workflows/ci.yml`):

- **Lint**: Code style validation with [Ruff](https://astral.sh/ruff).
- **dbt Parse**: Validates SQL models and macro syntax via `dbt parse` in Docker.
- **Dagster Check**: Generates dbt manifest and validates Dagster definitions via `dagster definitions validate -m dagster_project.definitions`.
