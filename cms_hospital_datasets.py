###### LINUX CRON JOB SCHEDULE EX:  0 2 * * * /usr/bin/python3 /path/to/cms_hospital_datasets.py
# Note:  The above will run at 2am system time daily

###### Libraries and Imports
import os
import re
import json
import requests
import pandas as pd
from datetime import datetime
from concurrent.futures import ThreadPoolExecutor
from io import StringIO  # Added for handling the CSV content from a string

###### Declare Constants

METASTORE_URL = "https://data.cms.gov/provider-data/api/1/metastore/schemas/dataset/items"
DATA_DIR = "hospital_datasets"
METADATA_FILE = "run_metadata.json"
MAX_WORKERS = 8

###### Ensure output directory exists
os.makedirs(DATA_DIR, exist_ok=True)

###### Load previous run metadata
if os.path.exists(METADATA_FILE):
    with open(METADATA_FILE, "r") as f:
        run_metadata = json.load(f)
else:
    run_metadata = {}

###### Helper functions

def to_snake_case(s):
    """Convert a string to snake_case."""
    s = re.sub(r"[’']", "", s)  # remove special apostrophes
    s = re.sub(r"[^\w\s]", "", s)  # remove special characters
    s = s.strip().lower().replace(" ", "_")
    s = re.sub(r"__+", "_", s)
    return s

def fetch_datasets():
    response = requests.get(METASTORE_URL)
    response.raise_for_status()
    print(response.json())
    return response.json()

def download_and_process(dataset):
    title = dataset["title"]
    updated_at = dataset["modified"]
    dataset_id = dataset["identifier"]

    # Check if updated
    last_run = run_metadata.get(dataset_id)
    if last_run and last_run >= updated_at:
        print(f"Skipping unchanged dataset: {title}")
        return

    print(f"Downloading: {title}")
    csv_url = dataset["distribution"][0]["downloadURL"]
    response = requests.get(csv_url)
    response.raise_for_status()

    # Load CSV into DataFrame
    df = pd.read_csv(StringIO(response.text))

    # Rename columns to snake_case
    df.columns = [to_snake_case(col) for col in df.columns]

    # Save to file
    safe_title = re.sub(r"[^\w]+", "_", title.lower())
    filename = f"{safe_title}.csv"
    df.to_csv(os.path.join(DATA_DIR, filename), index=False)

    # Update metadata
    run_metadata[dataset_id] = updated_at

###### Main function

def main():
    print("Fetching dataset metadata...")
    datasets = fetch_datasets()

    # Filter for "Hospitals" theme
    hospital_datasets = [ds for ds in datasets if "Hospitals" in ds.get("theme", [])]

    with ThreadPoolExecutor(max_workers=MAX_WORKERS) as executor:
        executor.map(download_and_process, hospital_datasets)

    # Save updated metadata
    with open(METADATA_FILE, "w") as f:
        json.dump(run_metadata, f, indent=2)

    print("Processing complete.")

###### Run Main function

if __name__ == "__main__":
    main()
