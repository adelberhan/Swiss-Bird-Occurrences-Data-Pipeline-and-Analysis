# DLT Ingestion Pipeline (`dlt_project`)

## Overview

The `dlt_project` component is responsible for the extraction and loading (EL) phase of the Swiss Bird Occurrences data platform. Using [dlt (data load tool)](https://dlthub.com/), it queries the public REST API of the **Global Biodiversity Information Facility (GBIF)**, normalizes the payloads, extracts nested media links, and loads the records into **Snowflake** under the `RAW_DATA` schema.

---

## Project Structure

```text
dlt_project/
├── __init__.py
├── config.py       # Defines the 24 target fields to keep from GBIF records
├── pipeline.py     # dlt source, resource, Snowflake destination, and execution entrypoint
└── README.md       # Component documentation
```

---

## Pipeline Specification

| Property                      | Value / Configuration                         |
| :---------------------------- | :-------------------------------------------- |
| **Pipeline Name**             | `swiss_bird_occurrences_v2`                   |
| **Source Function**           | `gbif_source`                                 |
| **Resource Name**             | `occurrences`                                 |
| **Target Dataset (Schema)**   | `RAW_DATA`                                    |
| **Primary Destination Table** | `OCCURRENCES_RAW`                             |
| **Child Table (Normalized)**  | `OCCURRENCES_RAW__ISSUES`                     |
| **Write Disposition**         | `replace` (full refresh on each pipeline run) |
| **Target Data Warehouse**     | Snowflake (`dlt.destinations.snowflake`)      |

### Source API & Extraction Logic

The pipeline targets the GBIF Occurrence Search API:

- **Endpoint**: `https://api.gbif.org/v1/occurrence/search`
- **Query Parameters**:
  - `country`: `CH` (Switzerland)
  - `year`: `2015,2026` (Occurrences observed between 2015 and 2026)
  - `classKey`: `212` (Taxonomic class _Aves_ / birds)
  - `limit`: `300` (records per API page)
  - `offset`: paginated sequentially
- **Extraction Cap**: Paginated up to `max_records = 1000` (or until `endOfRecords` is `true`).

### Field Transformation & Normalization

For each occurrence record returned by the GBIF API:

1. **Field Selection**: Only fields defined in `KEEP_FIELDS` (`dlt_project/config.py`) are kept:
   - Identifiers & metadata: `key`, `datasetKey`, `lastInterpreted`
   - Taxonomy: `acceptedScientificName`, `speciesKey`, `species`, `kingdom`, `class`, `order`, `family`, `genus`, `taxonRank`, `taxonomicStatus`
   - Temporal: `eventDate`, `year`, `month`, `day`
   - Spatial: `decimalLatitude`, `decimalLongitude`, `coordinateUncertaintyInMeters`, `countryCode`
   - Observation details: `basisOfRecord`, `occurrenceStatus`, `issues`
2. **Media Extraction**: Inspects the nested `media` array and extracts the first item's `identifier` as `media_url` (`cleaned_record["media_url"]`).
3. **Automated Nested List Normalization**: The `issues` attribute is a list of strings (e.g. `["GEODETIC_DATUM_ASSUMED_WGS84", "COORDINATE_ROUNDED"]`). `dlt` automatically normalizes this nested list into a relational child table named `OCCURRENCES_RAW__ISSUES` in Snowflake, assigning `_DLT_PARENT_ID` foreign keys referencing `_DLT_ID` of `OCCURRENCES_RAW`.

---

## Configuration & Environment Variables

DLT reads Snowflake connection credentials through environment variables (typically defined in the project `.env` file) or through `.dlt/secrets.toml`.

### Required Environment Variables

```env
# DLT Snowflake Destination Configuration
DESTINATION__SNOWFLAKE__CREDENTIALS__HOST=<your_account_identifier>.snowflakecomputing.com
DESTINATION__SNOWFLAKE__CREDENTIALS__DATABASE=BIRD_DATA_DB
DESTINATION__SNOWFLAKE__CREDENTIALS__USERNAME=<your_snowflake_username>
DESTINATION__SNOWFLAKE__CREDENTIALS__PASSWORD=<your_snowflake_password>
DESTINATION__SNOWFLAKE__CREDENTIALS__WAREHOUSE=COMPUTE_WH
DESTINATION__SNOWFLAKE__CREDENTIALS__ROLE=BIRD_DEV_ROLE
```

> [!NOTE]
> `enable_dataset_name_normalization=False` is explicitly set in `dlt_project/pipeline.py` to ensure Snowflake schema casing is preserved directly as `RAW_DATA`.

---

## Running DLT

### Local Execution (CLI)

Activate your virtual environment with the project root in your `PYTHONPATH`, then run `pipeline.py` directly:

```bash
# On Windows (PowerShell)
.\.venv\Scripts\Activate.ps1
$env:PYTHONPATH = "."
python -m dlt_project.pipeline
```

```bash
# On Linux/macOS
source .venv/bin/activate
export PYTHONPATH="."
python -m dlt_project.pipeline
```

### Expected Output

Upon completion, DLT prints a `LoadInfo` summary object displaying:

- Number of packages loaded
- Tables created or replaced (`OCCURRENCES_RAW`, `OCCURRENCES_RAW__ISSUES`, and DLT metadata tables such as `_dlt_loads`, `_dlt_version`, `_dlt_pipeline_state`)
- Execution duration and Snowflake target schema

---

## Integration with the Platform

- **Dagster Orchestration**: Wrapped directly as a software-defined asset named `gbif_dlt_asset` in `dagster_project/dagster_project/assets.py`. When Dagster triggers materialization, it invokes `pipeline.run(gbif_source())`.
- **Downstream dbt Consumption**: The resulting Snowflake table `BIRD_DATA_DB.RAW_DATA.OCCURRENCES_RAW` and child table `OCCURRENCES_RAW__ISSUES` serve as the raw data sources declared in `dbt-Swiss-Bird-Pipeline/dbt_project/models/curated/staging/sources.yml`.
