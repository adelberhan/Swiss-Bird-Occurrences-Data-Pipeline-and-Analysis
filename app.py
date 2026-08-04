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
        "COUNTRY" : COUNTRY,
        "year": f"{START_YEAR},{END_YEAR}",
        "LIMIT": LIMIT,
        "offset": offset
    }
    res = req.get(BASE_URL, params=params)
    res.raise_for_status() # Check for HTTP errors
    
    # If the status code is 200, return the JSON response
    return res.json()
    
    
