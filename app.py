from pathlib import Path
import json

import pandas as pd
import requests as req

#

# Declare constants
BASE_URL = "https://api.gbif.org/v1/occurrence/search"

COUNTRY = "CH"
START_YEAR = 2015
END_YEAR = 2026
TAXON_KEY = 212
LIMIT = 300

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


# Create folders
def create_folders():
    RAW_FOLDER.mkdir(parents=True, exist_ok=True)
    CSV_FOLDER.mkdir(parents=True, exist_ok=True)


# Fetch Pages
def fetch_pages(offset):
    params = {
        "COUNTRY": COUNTRY,
        "year": f"{START_YEAR},{END_YEAR}",
        "LIMIT": LIMIT,
        "offset": offset,
        "taxonKey": TAXON_KEY,
        
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

        #     to prevent requesting and the API max limit is less then 1000
        # if data["endOfRecords"]:
        #     print("End of records")
        #     break

        offset += LIMIT
        page += 1


# Load json files
def load_json_files():
    all_data = []
    
    for file_path in RAW_FOLDER.glob("*.json"):
        with open(file_path, "r", encoding="utf-8") as file:
            data = json.load(file)
        all_data.extend(data["results"])
    return all_data


# Extract media URL from the media field
def extract_media_url(media_url):
    if not media_url :
        return ""
    return media_url[0].get("identifier", "")



# if __name__ == "__main__":
#     main()
