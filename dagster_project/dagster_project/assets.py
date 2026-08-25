import os
from pathlib import Path

# DLT project root
PROJECT_ROOT = Path(__file__).resolve().parents[2]
os.environ["DLT_PROJECT_DIR"] = str(PROJECT_ROOT)

import dagster as dg

from dlt_pipeline.pipeline import pipeline, gbif_source


@dg.asset
def gbif_dlt_asset():
    load_info = pipeline.run(gbif_source())
    return load_info