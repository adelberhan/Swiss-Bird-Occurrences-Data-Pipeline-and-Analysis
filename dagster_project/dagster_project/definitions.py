import dagster as dg

from dagster_project.assets import gbif_dlt_asset
from dagster_project.dbt_assets import swiss_bird_dbt_assets, dbt_resource


# Job that materializes the whole pipeline
bird_pipeline_job = dg.define_asset_job(
    name="bird_pipeline_job",
    selection=dg.AssetSelection.all(),
)


# Run the job once every day
bird_daily_schedule = dg.ScheduleDefinition(
    job=bird_pipeline_job,
    cron_schedule="0 2 * * *",
)


defs = dg.Definitions(
    assets=[
        gbif_dlt_asset,
        swiss_bird_dbt_assets,
    ],
    resources={
        "dbt": dbt_resource,
    },
    jobs=[
        bird_pipeline_job,
    ],
    schedules=[
        bird_daily_schedule,
    ],
)