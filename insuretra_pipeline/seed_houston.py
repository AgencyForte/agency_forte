from __future__ import annotations

import logging
from dotenv import load_dotenv

from insuretra_pipeline.config import DATASETS, get_settings
from insuretra_pipeline.db import (
    connect,
    consolidate_master_sql,
    create_pipeline_run,
    finish_pipeline_run,
    reset_staging_and_load,
    log,
)
from insuretra_pipeline.ingest import fetch_and_normalize

# Houston and contiguous counties
HOUSTON_COUNTIES = (
    "'Harris', 'Montgomery', 'Liberty', 'Chambers', "
    "'Galveston', 'Brazoria', 'Fort Bend', 'Waller'"
)

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")


def tag_houston_target_zone(conn) -> None:
    logging.info("Applying PostGIS spatial filter for Greater Houston zone...")
    
    # Tag agencies
    conn.execute(
        f"""
        UPDATE master_agencies m
        SET in_target_zone = TRUE
        FROM texas_zip_geo z
        WHERE m.physical_zip = z.zip
          AND z.county IN ({HOUSTON_COUNTIES})
        """
    )
    
    # Tag agents
    conn.execute(
        f"""
        UPDATE master_agents m
        SET in_target_zone = TRUE
        FROM texas_zip_geo z
        WHERE m.postal_code = z.zip
          AND z.county IN ({HOUSTON_COUNTIES})
        """
    )
    conn.commit()


def main() -> None:
    load_dotenv()
    settings = get_settings()
    if not settings.database_url:
        raise SystemExit("DATABASE_URL is required.")

    staged = {}
    
    logging.info("Phase 1: Data Extraction & Polars Parsing...")
    for dataset_key in DATASETS:
        logging.info(f"Extracting {dataset_key} from Socrata API...")
        table, rows = fetch_and_normalize(dataset_key)
        staged[dataset_key] = (table, rows)
        logging.info(f"Loaded {len(rows)} records into Polars dataframe for {dataset_key}.")

    logging.info("Connecting to PostgreSQL Master Database...")
    with connect(settings.database_url) as conn:
        run_id = create_pipeline_run(conn)
        log(conn, run_id, "info", "Seed Houston script started (Dump Guard bypassed).")
        
        try:
            logging.info("Phase 2: Overriding Staging Tables (High-Speed COPY)...")
            reset_staging_and_load(conn, staged)
            
            logging.info("Phase 3: Master State Consolidation...")
            consolidate_master_sql(conn)
            
            # Phase 4: Geo Targeting
            tag_houston_target_zone(conn)
            
            # Finish run
            finish_pipeline_run(conn, run_id, "succeeded", 0, "Initial Houston seeding completed.")
            logging.info("Day Zero Houston Seeding completed successfully.")
            
        except Exception as exc:
            log(conn, run_id, "error", f"Seed failed: {exc}")
            finish_pipeline_run(conn, run_id, "failed", None, str(exc))
            logging.error(f"Seeding failed: {exc}")
            raise


if __name__ == "__main__":
    main()
