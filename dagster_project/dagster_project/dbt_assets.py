from pathlib import Path

import dagster as dg
from dagster_dbt import (
    DagsterDbtTranslator,
    DbtCliResource,
    dbt_assets,
)

PROJECT_ROOT = Path(__file__).resolve().parents[2]

DBT_PROJECT_DIR = (
    PROJECT_ROOT
    / "dbt-Swiss-Bird-Pipeline"
    / "dbt_project"
)

DBT_MANIFEST_PATH = DBT_PROJECT_DIR / "target" / "manifest.json"

print(f"DBT PROJECT DIR: {DBT_PROJECT_DIR}")
print(f"DBT MANIFEST PATH: {DBT_MANIFEST_PATH}")
print(f"PROJECT EXISTS: {DBT_PROJECT_DIR.exists()}")
print(f"MANIFEST EXISTS: {DBT_MANIFEST_PATH.exists()}")


class CustomDagsterDbtTranslator(DagsterDbtTranslator):

    def get_asset_key(self, dbt_resource_props):
        resource_type = dbt_resource_props.get("resource_type")
        resource_name = dbt_resource_props.get("name")

        if resource_type == "source" and resource_name == "OCCURRENCES_RAW":
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