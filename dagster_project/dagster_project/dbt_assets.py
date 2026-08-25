from typing import Any, Mapping

import dagster as dg
from dagster_dbt import (
    DagsterDbtTranslator,
    DbtCliResource,
    dbt_assets,
)

DBT_PROJECT_DIR = (
    "D:/Docements/WWF/wilddata/"
    "dbt-Swiss-Bird-Occurrences-Data-Pipeline-and-Analysis/"
    "bird_project_week2"
)

DBT_MANIFEST_PATH = f"{DBT_PROJECT_DIR}/target/manifest.json"


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
    project_dir=DBT_PROJECT_DIR,
)


@dbt_assets(
    manifest=DBT_MANIFEST_PATH,
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
