from __future__ import annotations

from dataclasses import dataclass
import os


@dataclass(frozen=True)
class DatasetConfig:
    key: str
    resource_id: str
    staging_table: str


DATASETS: dict[str, DatasetConfig] = {
    "agency_appointments": DatasetConfig("agency_appointments", "avjc-7u2m", "stage_agency_appointments"),
    "agent_appointments": DatasetConfig("agent_appointments", "ft7p-v8a7", "stage_agent_appointments"),
    "relationships": DatasetConfig("relationships", "kvqi-vsrr", "stage_agent_agency_links"),
    "agencies": DatasetConfig("agencies", "3yqc-fcdt", "stage_agencies"),
}

DATASET_ALIASES = {
    "all": tuple(DATASETS.keys()),
    "agency-appointments": ("agency_appointments",),
    "agent-appointments": ("agent_appointments",),
    "relationships": ("relationships",),
    "agencies": ("agencies",),
}


@dataclass(frozen=True)
class Settings:
    database_url: str | None
    socrata_app_token: str | None
    dump_guard_threshold: int
    ops_webhook_url: str | None


def get_settings() -> Settings:
    return Settings(
        database_url=os.getenv("DATABASE_URL"),
        socrata_app_token=os.getenv("SOCRATA_APP_TOKEN"),
        dump_guard_threshold=int(os.getenv("DUMP_GUARD_THRESHOLD", "1500")),
        ops_webhook_url=os.getenv("OPS_WEBHOOK_URL"),
    )


def resolve_dataset_keys(dataset: str) -> tuple[str, ...]:
    if dataset in DATASET_ALIASES:
        return DATASET_ALIASES[dataset]
    if dataset in DATASETS:
        return (dataset,)
    raise ValueError(f"Unknown dataset '{dataset}'. Expected one of: {', '.join(DATASET_ALIASES)}")

