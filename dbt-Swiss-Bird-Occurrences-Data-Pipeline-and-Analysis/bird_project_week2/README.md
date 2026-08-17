# Swiss Bird Occurrences Data Pipeline — Week 2

## Overview

Week 2 extends the Swiss Bird Occurrences project from Week 1 into a Snowflake and dbt analytics engineering pipeline.

The Week 1 GBIF bird occurrence CSV is loaded into Snowflake and transformed through three production-style layers:

```text
RAW_DATA → CURATED → SERVING
```

The pipeline currently works with 1,000 Swiss bird occurrence records.

## Architecture

```text
Week 1 CSV
    │
    ▼
RAW_DATA
└── OCCURRENCES_RAW
        │
     source()
        ▼
CURATED
├── stg_occurrences
│      ├── dim_species
│      ├── dim_dataset
│      └── fct_occurrences
│              │
              ref()
              ▼
SERVING
├── species_occurrence_summary
├── occurrences_by_year
└── data_quality_summary
```

## Snowflake Setup

- Database: `BIRD_DATA_DB`
- Development role: `BIRD_DEV_ROLE`
- Warehouse: `COMPUTE_WH`
- Schemas:
  - `RAW_DATA`
  - `CURATED`
  - `SERVING`

The development work is performed using `BIRD_DEV_ROLE` rather than `ACCOUNTADMIN`.

## Raw Data

The Week 1 CSV data is loaded into:

```text
BIRD_DATA_DB.RAW_DATA.OCCURRENCES_RAW
```

The table contains the 24 required GBIF occurrence fields plus the derived `media_url` field from Week 1.

The current dataset contains 1,000 records.

## Project Structure

```text
week2/
│
├── dbt_project.yml
├── macros/
│   └── generate_schema_name.sql
│
├── models/
│   ├── curated/
│   │   ├── staging/
│   │   │   ├── sources.yml
│   │   │   ├── stg_occurrences.sql
│   │   │   └── schema.yml
│   │   ├── dimensions/
│   │   │   ├── dim_species.sql
│   │   │   ├── dim_dataset.sql
│   │   │   └── schema.yml
│   │   └── facts/
│   │       ├── fct_occurrences.sql
│   │       └── schema.yml
│   │
│   └── serving/
│       ├── species_occurrence_summary.sql
│       ├── occurrences_by_year.sql
│       └── data_quality_summary.sql
│
├── analyses/
├── seeds/
├── snapshots/
└── tests/
```

## Curated Layer

### `stg_occurrences`

One row per `occurrence_key`.

Responsibilities:

- Read from the `OCCURRENCES_RAW` dbt source.
- Convert names to `snake_case`.
- Cast values to appropriate Snowflake data types.
- Standardize the raw occurrence records.

Materialization: **view**

Tests:

- `occurrence_key` is not null.
- `occurrence_key` is unique.

### `dim_species`

One row per `species_key`.

Columns:

```text
species_key
accepted_scientific_name
species_name
kingdom
taxon_class
taxon_order
family
genus
taxon_rank
taxonomic_status
```

The model uses `ROW_NUMBER()` partitioned by `species_key` to deduplicate records and prioritize accepted taxonomic records.

Materialization: **table**

Tests:

- `species_key` is not null.
- `species_key` is unique.

### `dim_dataset`

One row per `dataset_key`.

Columns:

```text
dataset_key
record_count
first_seen
last_seen
```

`record_count`, `first_seen`, and `last_seen` are calculated from the occurrence records.

The second GBIF `/dataset/{key}` extract for dataset title was intentionally excluded from this version.

Materialization: **table**

Tests:

- `dataset_key` is not null.
- `dataset_key` is unique.

### `fct_occurrences`

One row per `occurrence_key`.

Columns:

```text
occurrence_key
species_key
dataset_key
event_date
year
month
day
decimal_latitude
decimal_longitude
coordinate_uncertainty_m
country_code
basis_of_record
occurrence_status
media_url
has_media
issues
```

`has_media` is derived from `media_url`.

Foreign-key relationships are tested against `dim_species` and `dim_dataset`.

Materialization: **table**

Tests:

- `occurrence_key` is not null.
- `occurrence_key` is unique.
- `species_key` exists in `dim_species`.
- `dataset_key` exists in `dim_dataset`.

## Serving Layer

### `species_occurrence_summary`

One row per species.

Columns:

```text
species_key
occurrence_count
first_observed
last_observed
dataset_count
pct_with_coordinates
```

### `occurrences_by_year`

One row per `species_key × year`.

Columns:

```text
species_key
year
occurrence_count
```

### `data_quality_summary`

One row per issue flag.

Columns:

```text
issue
record_count
pct_of_total
```

## Materialization Strategy

| Layer | Model | Materialization |
|---|---|---|
| CURATED | `stg_occurrences` | View |
| CURATED | Dimensions | Table |
| CURATED | Fact | Table |
| SERVING | Serving models | Table |

## Data Tests

The project contains 8 dbt tests covering:

- `stg_occurrences.occurrence_key`: `not_null`, `unique`
- `dim_species.species_key`: `not_null`, `unique`
- `dim_dataset.dataset_key`: `not_null`, `unique`
- `fct_occurrences.occurrence_key`: `not_null`, `unique`
- `fct_occurrences.species_key`: relationship to `dim_species`
- `fct_occurrences.dataset_key`: relationship to `dim_dataset`

## Running the Project

The project uses the `bird_project_week2` profile configured in:

```text
~/.dbt/profiles.yml
```

Validate the connection:

```bash
dbt debug
```

Parse the project:

```bash
dbt parse
```

Build all models and tests:

```bash
dbt build
```

Run a specific model:

```bash
dbt run --select stg_occurrences
```

Run tests:

```bash
dbt test
```

The final successful build currently produces:

```text
7 models
8 tests
15 total
15 success
```

## Documentation

This project uses dbt Fusion.

For the current Fusion version, `dbt docs generate` is not supported. The catalog can be generated with:

```bash
dbt compile --write-catalog
```

This writes `catalog.json` to the target directory.

## Project Status

Week 2 implementation is complete for the selected scope.

Completed:

- Snowflake database and schemas
- Development role and warehouse
- Week 1 CSV loaded into `RAW_DATA`
- dbt project connected to Snowflake
- dbt source configuration
- Curated staging model
- Species dimension
- Dataset dimension
- Occurrence fact
- Serving models
- Data quality summary
- dbt tests
- Successful full `dbt build`

### Intentional Scope Decision

The original requirement specified a second GBIF extract from `/dataset/{key}` to obtain the dataset title.

For this Week 2 implementation, that second extract and dataset title were intentionally excluded.

Therefore `dim_dataset` contains:

```text
dataset_key
record_count
first_seen
last_seen
```

## Technologies

- GBIF API — source data
- Python / pandas — Week 1 data preparation
- Snowflake — data warehouse
- dbt Fusion — transformation, modeling, and testing
- SQL — transformations and analytics
- Git / GitHub — version control
