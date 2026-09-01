from collections.abc import Mapping
from pathlib import Path
from typing import Any

import dagster as dg
from dagster_dbt import (
    DagsterDbtTranslator,
    DbtCliResource,
    dbt_assets,
)

# Project root:
# /app when running inside Docker
# project root when running locally

PROJECT_ROOT = Path(__file__).resolve().parents[2]

DBT_PROJECT_DIR = (
    PROJECT_ROOT
    / "dbt-Swiss-Bird-Occurrences-Data-Pipeline-and-Analysis"
    / "bird_project_week2"
)

DBT_MANIFEST_PATH = DBT_PROJECT_DIR / "target" / "manifest.json"


class CustomDagsterDbtTranslator(DagsterDbtTranslator):

    def get_asset_key(
        self,
        dbt_resource_props: Mapping[str, Any],
    ) -> dg.AssetKey:

        # Map the dbt source OCCURRENCES_RAW
        # to the Dagster DLT asset
        if (
            dbt_resource_props.get("resource_type") == "source"
            and dbt_resource_props.get("name") == "OCCURRENCES_RAW"
        ):
            return dg.AssetKey(["gbif_dlt_asset"])

        return super().get_asset_key(dbt_resource_props)


dbt_resource = DbtCliResource(
    project_dir=str(DBT_PROJECT_DIR),
)


@dbt_assets(
    manifest=str(DBT_MANIFEST_PATH),
    dagster_dbt_translator=CustomDagsterDbtTranslator(),
)
def swiss_bird_dbt_assets(
    context: dg.AssetExecutionContext,
    dbt: DbtCliResource,
):
    yield from dbt.cli(
        ["build"],
        context=context,
    ).stream()
