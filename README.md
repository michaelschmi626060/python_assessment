# CMS Hospital Dataset Downloader

This Python script automates the download and processing of **CMS Hospital datasets** from the [data.cms.gov](https://data.cms.gov/) API. It fetches only the latest datasets under the "Hospitals" theme and saves them as CSV files with standardized column names in snake_case format.

---

## 🛠 Features

- Downloads only *new or updated* datasets.
- Standardizes column names to `snake_case`.
- Saves datasets locally in a designated folder.
- Maintains metadata to skip already downloaded datasets.
- Runs in parallel for efficiency (multithreaded).
- Designed to be scheduled via a Linux `cron` job.

---

## 📦 Dependencies

Ensure the following Python packages are installed:

```bash
pip install pandas requests
