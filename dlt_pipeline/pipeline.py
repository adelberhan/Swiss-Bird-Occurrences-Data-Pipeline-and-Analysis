import dlt
import requests
from .config import KEEP_FIELDS


@dlt.resource(
    name="occurrences",
    table_name="OCCURRENCES_RAW",
)
def occurrences():
    url = "https://api.gbif.org/v1/occurrence/search"

    offset = 0
    page_size = 300
    max_records = 1000

    while offset < max_records:
        params = {
            "country": "CH",
            "year": "2015,2026",
            "classKey": 212,
            "limit": page_size,
            "offset": offset,
        }

        response = requests.get(url, params=params)
        response.raise_for_status()

        data = response.json()
        results = data["results"]

        if not results:
            break

        for record in results[: max_records - offset]:
            cleaned_record = {field: record.get(field) for field in KEEP_FIELDS}

            media = record.get("media", [])

            cleaned_record["media_url"] = media[0].get("identifier") if media else None

            yield cleaned_record

        if data["endOfRecords"]:
            break

        offset += page_size


@dlt.source
def gbif_source():
    return occurrences


destination = dlt.destinations.snowflake(enable_dataset_name_normalization=False)

pipeline = dlt.pipeline(
    pipeline_name="swiss_bird_occurrences_v2",
    destination=destination,
    dataset_name="RAW_DATA",
)


if __name__ == "__main__":
    load_info = pipeline.run(gbif_source())

    print(load_info)
