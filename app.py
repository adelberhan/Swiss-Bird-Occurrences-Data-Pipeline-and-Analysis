from pathlib import Path
import json

import pandas as pd
import requests as req

#

# Declare constants
# Declare constants values

# Declare constants values

BASE_URL = "https://api.gbif.org/v1/occurrence/search"

COUNTRY = "CH"
YEAR = 2015


LIMIT = 300
CLASS_KEY = 212

RAW_FOLDER = Path("data/raw")
CSV_FOLDER = Path("data/csv")

KEEP_FIELDS = [
    "key",
    "datasetKey",
    "lastInterpreted",
    "acceptedScientificName",
    "speciesKey",
    "species",
    "kingdom",
    "class",
    "order",
    "family",
    "genus",
    "taxonRank",
    "taxonomicStatus",
    "eventDate",
    "year",
    "month",
    "day",
    "decimalLatitude",
    "decimalLongitude",
    "coordinateUncertaintyInMeters",
    "countryCode",
    "basisOfRecord",
    "occurrenceStatus",
    "issues",
]

FIELD_RENAMED = {
    "key": "gbif_occurrence_id",
    "datasetKey": "dataset_uuid",
    "lastInterpreted": "gbif_last_processed_at",
    "acceptedScientificName": "accepted_scientific_name",
    "speciesKey": "species_taxon_id",
    "species": "species_name",
    "kingdom": "kingdom_name",
    "class": "class_name",
    "order": "order_name",
    "family": "family_name",
    "genus": "genus_name",
    "taxonRank": "taxonomic_rank",
    "taxonomicStatus": "taxonomic_status",
    "eventDate": "observation_datetime",
    "year": "observation_year",
    "month": "observation_month",
    "day": "observation_day",
    "decimalLatitude": "latitude",
    "decimalLongitude": "longitude",
    "coordinateUncertaintyInMeters": "coordinate_uncertainty_meters",
    "countryCode": "country_iso_code",
    "basisOfRecord": "record_basis_type",
    "occurrenceStatus": "presence_status",
    "issues": "data_quality_issues",
}

# Create folders
def create_folders():
    RAW_FOLDER.mkdir(parents=True, exist_ok=True)
    CSV_FOLDER.mkdir(parents=True, exist_ok=True)


# Fetch Pages [by calling the API with offset]
def fetch_pages(offset):
    params = {
        "country": COUNTRY,
        "year": YEAR,
        "limit": LIMIT,
        "classKey": CLASS_KEY,
        "offset": offset,
    }
    res = req.get(BASE_URL, params=params)
    res.raise_for_status()  # Check for HTTP errors

    # If the status code is 200, return the JSON response
    return res.json()


# Load all pages
def load_all_pages():
    offset = 0
    page = 1

    while offset < 1000:  # download max 1000

        print(f"Fetching page {page} with offset {offset}")
        data = fetch_pages(offset)
        file_path = RAW_FOLDER / f"page_{page}.json"

        with open(file_path, "w", encoding="utf-8") as file:
            json.dump(data, file, ensure_ascii=False, indent=2)

        offset += LIMIT
        page += 1


def load_json_files():
    all_data = []

    for file_path in RAW_FOLDER.glob(
        "*.json"
    ):  # to search inside the folder for all json files
        with open(file_path, "r", encoding="utf-8") as file:
            data = json.load(file)

        all_data.extend(
            data["results"]
        )  # collect all results from each file into a single list
    return all_data


# Extract media URL from the media field
def extract_media_url(media_url):
    if not media_url:
        return ""
    return media_url[0].get("identifier", "")


# Clean dataframe by loading json files and extracting only the fields we want to keep
def clean_dataframe(records):
    cleaned_records = []

    # Looping through each record in json file
    # and creating a new dictionary with only the fields we want to keep
    for record in records:
        raw = {}

        # Keeping only the fields we want to keep
        for field in KEEP_FIELDS:
            raw[field] = record.get(field)

        # Extracting media URL from the media field
        raw["media_url"] = extract_media_url(record.get("media"))

        # rename the columns
        cleaned_records.append(raw)

    df = pd.DataFrame(cleaned_records)
    return df.rename(columns=FIELD_RENAMED)

# Save as csv file

def save_as_csv(df):
    output = CSV_FOLDER / "swiss_bird_occurrences.csv"

    df.to_csv(output, index=False)

    print(f"Data saved to {output}")


def main():
    create_folders()

    load_all_pages()

    records = load_json_files()

    df = clean_dataframe(records)
    df = df.head(1000)  # Limit to 1000 records
    save_as_csv(df)

    print(df.head())


if __name__ == "__main__":
    main()
