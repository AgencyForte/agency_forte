from __future__ import annotations

import os
import tempfile
import requests
import polars as pl

from .config import DatasetConfig


def fetch_dataset_rows(config: DatasetConfig, app_token: str | None) -> pl.DataFrame:
    headers = {"X-App-Token": app_token} if app_token else {}
    url = f"https://data.texas.gov/api/views/{config.resource_id}/rows.csv?accessType=DOWNLOAD"
    
    with tempfile.NamedTemporaryFile(suffix=".csv", delete=False) as tmp:
        with requests.get(url, headers=headers, stream=True, timeout=600) as r:
            r.raise_for_status()
            for chunk in r.iter_content(chunk_size=8192):
                tmp.write(chunk)
        tmp_path = tmp.name

    try:
        return pl.read_csv(
            tmp_path,
            infer_schema_length=10000,
            null_values=["", "NA", "None", "null"],
            ignore_errors=True
        )
    finally:
        if os.path.exists(tmp_path):
            try:
                os.remove(tmp_path)
            except PermissionError:
                pass
