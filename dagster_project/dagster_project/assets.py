import sys
from pathlib import Path

# DLT project root
PROJECT_ROOT = Path(__file__).resolve().parents[2]
# os.environ["DLT_PROJECT_DIR"] = str(PROJECT_ROOT)
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))
    
import dagster as dg

# pyrefly: ignore [missing-import]
from dlt_project.pipeline import gbif_source, pipeline


@dg.asset
def gbif_dlt_asset():
    """Run the DLT pipeline to ingest GBIF bird occurrence data."""
    load_info = pipeline.run(gbif_source())
    return load_info
