from __future__ import annotations

import logging
from dotenv import load_dotenv

from insuretra_pipeline.config import get_settings
from insuretra_pipeline.db import connect, generate_events_sql, process_events_geo, truncate_staging

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")


def main() -> None:
    load_dotenv()
    settings = get_settings()
    if not settings.database_url:
        raise SystemExit("DATABASE_URL is required.")

    with connect(settings.database_url) as conn:
        logging.info("Connected to database. Starting Competitor Bleeding simulation...")

        # 1. Live Target Selection or Insertion
        mock_agent_npn = "MOCK_VET_9999"
        mock_agency_id = "MOCK_AGENCY_9999"
        mock_zip = "78701"
        mock_hash = "MOCK_HASH_123"

        # Check if we can find an existing active veteran relationship in the target zone
        existing = conn.execute(
            """
            SELECT m.agent_npn, m.agency_tdi_id, a.physical_zip, m.structural_hash
            FROM master_agent_agency_links m
            JOIN master_agencies a ON a.agency_tdi_id = m.agency_tdi_id
            JOIN master_agents ag ON ag.agent_npn = m.agent_npn
            WHERE m.is_active = TRUE
              AND LOWER(m.association_type) = 'sub-agent'
              AND a.in_target_zone = TRUE
              AND (
                DATE_PART('year', AGE(CURRENT_DATE, COALESCE(m.relationship_started_at, m.first_seen_date))) * 12
                + DATE_PART('month', AGE(CURRENT_DATE, COALESCE(m.relationship_started_at, m.first_seen_date)))
              ) >= 24
            LIMIT 1
            """
        ).fetchone()

        inserted_mock = False
        if existing:
            target_agent_npn = existing["agent_npn"]
            target_agency_id = existing["agency_tdi_id"]
            target_zip = existing["physical_zip"]
            target_hash = existing["structural_hash"]
            logging.info(f"Found existing live target -> Agent: {target_agent_npn}, Agency: {target_agency_id}")
        else:
            logging.info("No live target found. Inserting mock veteran relationship...")
            inserted_mock = True
            target_agent_npn = mock_agent_npn
            target_agency_id = mock_agency_id
            target_zip = mock_zip
            target_hash = mock_hash

            # Insert mock geo for the zip if it doesn't exist
            conn.execute(
                """
                INSERT INTO texas_zip_geo (zip, county, centroid, geometry)
                VALUES (%s, 'Harris', ST_SetSRID(ST_MakePoint(-95.3698, 29.7604), 4326), ST_SetSRID(ST_MakePoint(-95.3698, 29.7604), 4326))
                ON CONFLICT (zip) DO NOTHING
                """,
                (target_zip,)
            )

            # Insert mock agency
            conn.execute(
                """
                INSERT INTO master_agencies (agency_tdi_id, name, physical_zip, in_target_zone)
                VALUES (%s, 'Mock Competitor Agency', %s, TRUE)
                ON CONFLICT DO NOTHING
                """,
                (target_agency_id, target_zip)
            )

            # Insert mock agent
            conn.execute(
                """
                INSERT INTO master_agents (agent_npn, full_name, in_target_zone)
                VALUES (%s, 'Mock Veteran Agent', TRUE)
                ON CONFLICT DO NOTHING
                """,
                (target_agent_npn,)
            )

            # Insert mock linkage (>3 years old)
            conn.execute(
                """
                INSERT INTO master_agent_agency_links (
                    agent_npn, agency_tdi_id, association_type, relationship_started_at, 
                    first_seen_date, last_seen_date, structural_hash, is_active
                ) VALUES (%s, %s, 'Sub-Agent', CURRENT_DATE - INTERVAL '3 years', 
                          CURRENT_DATE - INTERVAL '3 years', CURRENT_DATE, %s, TRUE)
                ON CONFLICT DO NOTHING
                """,
                (target_agent_npn, target_agency_id, target_hash)
            )

        # 2. Staging State Simulation
        logging.info("Simulating staging state (Producer vanishing)...")
        tables_to_truncate = [
            "stage_agencies",
            "stage_agent_agency_links",
            "stage_agency_appointments",
            "stage_agent_appointments",
        ]
        truncate_staging(conn, tables_to_truncate)

        # To simulate vanishing, we explicitly do NOT insert the target_hash into stage_agent_agency_links.
        # Since it's empty, the relationship is effectively absent from staging.

        # 3. Event Generation Engine Execution
        logging.info("Executing standard event generation pipeline...")
        generate_events_sql(conn)

        # Verify event creation
        event_row = conn.execute(
            """
            SELECT event_id, event_type, payload, is_processed
            FROM market_timeline
            WHERE target_agent_npn = %s AND event_type = 'COMPETITOR_BLEEDING'
            """,
            (target_agent_npn,)
        ).fetchone()

        assert event_row is not None, "Alert was not generated in market_timeline!"
        logging.info("SUCCESS: Competitor Bleeding threat row successfully identified and written to market_timeline.")

        # 4. Post-Processing Geo-Routing Execution
        logging.info("Executing PostGIS Geo-Routing post-processing...")
        process_events_geo(conn)

        # Verify payload mutation
        processed_event = conn.execute(
            """
            SELECT is_processed, payload
            FROM market_timeline
            WHERE event_id = %s
            """,
            (event_row["event_id"],)
        ).fetchone()

        assert processed_event["is_processed"] is True, "Event was not flagged as is_processed=TRUE."
        payload = processed_event["payload"]
        assert "geo_routing" in payload, "geo_routing block is missing from payload."
        assert payload["geo_routing"].get("processed") is True, "geo_routing 'processed' boolean is missing or false."
        assert payload["geo_routing"].get("zip") == target_zip, "geo_routing 'zip' does not match target zip."
        
        logging.info("SUCCESS: Payload correctly mutated with geographic indexing.")

        # 5. Verification Assertions & Clean up
        logging.info("Rolling back transaction to pristine state...")
        if inserted_mock:
            conn.execute("DELETE FROM market_timeline WHERE target_agent_npn = %s", (target_agent_npn,))
            conn.execute("DELETE FROM master_agent_agency_links WHERE agent_npn = %s", (target_agent_npn,))
            conn.execute("DELETE FROM master_agents WHERE agent_npn = %s", (target_agent_npn,))
            conn.execute("DELETE FROM master_agencies WHERE agency_tdi_id = %s", (target_agency_id,))
        else:
            # Delete just the timeline event generated by the live run
            conn.execute("DELETE FROM market_timeline WHERE event_id = %s", (event_row["event_id"],))

        # Re-truncate staging
        truncate_staging(conn, tables_to_truncate)

        conn.commit()
        logging.info("Cleanup complete. Simulation script finished successfully.")


if __name__ == "__main__":
    main()
