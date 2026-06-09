from __future__ import annotations

import argparse
from dotenv import load_dotenv

import polars as pl

from .config import DATASETS, get_settings, resolve_dataset_keys
from .db import connect, reset_staging_and_load
from .normalize import normalize_rows
from .socrata import fetch_dataset_rows


def fetch_and_normalize(dataset_key: str) -> tuple[str, pl.DataFrame]:
    settings = get_settings()
    dataset = DATASETS[dataset_key]
    raw_rows = fetch_dataset_rows(dataset, settings.socrata_app_token)
    return dataset.staging_table, normalize_rows(dataset_key, raw_rows)


def main() -> None:
    load_dotenv()
    parser = argparse.ArgumentParser(description="Fetch TDI Socrata datasets and load Insuretra staging tables.")
    parser.add_argument("--dataset", default="all", help="Dataset key or all.")
    args = parser.parse_args()

    settings = get_settings()
    if not settings.database_url:
        raise SystemExit("DATABASE_URL is required to load staging tables.")

    staged = {}
    for dataset_key in resolve_dataset_keys(args.dataset):
        table, rows = fetch_and_normalize(dataset_key)
        staged[dataset_key] = (table, rows)
        print(f"{dataset_key}: fetched {len(rows)} normalized rows")

    with connect(settings.database_url) as conn:
        reset_staging_and_load(conn, staged)


if __name__ == "__main__":
    main()

