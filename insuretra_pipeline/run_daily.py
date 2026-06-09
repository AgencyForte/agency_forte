from __future__ import annotations

from dotenv import load_dotenv

from .config import DATASETS, get_settings
from .db import (
    anomaly,
    connect,
    consolidate_master_sql,
    create_pipeline_run,
    finish_pipeline_run,
    generate_events_sql,
    get_master_counts,
    get_stage_counts,
    log,
    reset_staging_and_load,
)
from .events import dump_guard_breached
from .ingest import fetch_and_normalize


def main() -> None:
    load_dotenv()
    settings = get_settings()
    if not settings.database_url:
        raise SystemExit("DATABASE_URL is required.")

    staged = {}
    for dataset_key in DATASETS:
        table, rows = fetch_and_normalize(dataset_key)
        staged[dataset_key] = (table, rows)

    with connect(settings.database_url) as conn:
        run_id = create_pipeline_run(conn)
        try:
            reset_staging_and_load(conn, staged)
            stage_counts = get_stage_counts(conn)
            master_counts = get_master_counts(conn)
            breached, delta = dump_guard_breached(stage_counts, master_counts, settings.dump_guard_threshold)
            log(conn, run_id, "info", "Loaded staging tables.", {"stage_counts": stage_counts, "master_counts": master_counts})

            if breached:
                anomaly(
                    conn,
                    run_id,
                    "BULK_UPDATE_QUARANTINE",
                    f"Statewide row delta {delta} exceeded threshold {settings.dump_guard_threshold}.",
                    metadata={"stage_counts": stage_counts, "master_counts": master_counts},
                )
                consolidate_master_sql(conn)
                finish_pipeline_run(conn, run_id, "quarantined", delta, "Dump guard breached; event generation skipped.")
                return

            generate_events_sql(conn)
            consolidate_master_sql(conn)
            finish_pipeline_run(conn, run_id, "succeeded", delta, "Pipeline completed.")
        except Exception as exc:
            log(conn, run_id, "error", str(exc))
            finish_pipeline_run(conn, run_id, "failed", None, str(exc))
            raise


if __name__ == "__main__":
    main()

