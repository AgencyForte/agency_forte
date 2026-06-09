from __future__ import annotations

import requests

from .config import DatasetConfig


def fetch_dataset_rows(config: DatasetConfig, app_token: str | None, page_size: int = 50_000) -> list[dict]:
    headers = {"X-App-Token": app_token} if app_token else {}
    offset = 0
    rows: list[dict] = []
    while True:
        response = requests.get(
            f"https://data.texas.gov/resource/{config.resource_id}.json",
            headers=headers,
            params={"$limit": page_size, "$offset": offset},
            timeout=60,
        )
        response.raise_for_status()
        batch = response.json()
        if not batch:
            break
        rows.extend(batch)
        if len(batch) < page_size:
            break
        offset += page_size
    return rows

