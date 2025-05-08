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
    try:
        csv_url = dataset["distribution"][0]["downloadURL"]
        response = requests.get(csv_url)
        response.raise_for_status()  # Ensure we don't continue if there's a problem with the request
    except requests.exceptions.RequestException as e:
        print(f"Error downloading {title}: {e}")
        return

    # Load CSV into DataFrame
    try:
        df = pd.read_csv(StringIO(response.text))
    except Exception as e:
        print(f"Error processing {title}: {e}")
        return

    # Rename columns to snake_case
    df.columns = [to_snake_case(col) for col in df.columns]

    # Save to file
    safe_title = re.sub(r"[^\w]+", "_", title.lower())
    filename = f"{safe_title}.csv"
    try:
        df.to_csv(os.path.join(DATA_DIR, filename), index=False)
    except Exception as e:
        print(f"Error saving file for {title}: {e}")
        return

    # Update metadata
    run_metadata[dataset_id] = updated_at
