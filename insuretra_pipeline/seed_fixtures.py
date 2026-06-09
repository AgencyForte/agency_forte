from __future__ import annotations

from datetime import date
from dotenv import load_dotenv

from .config import get_settings
from .db import connect, generate_events_sql, reset_staging_and_load
from .hashing import structural_hash


def fixture_rows() -> dict[str, tuple[str, list[dict]]]:
    old_hash = structural_hash("9001", "npn:agency-old", "Sub-Agent")
    short_hash = structural_hash("9002", "npn:agency-short", "Sub-Agent")
    active_hash = structural_hash("9003", "npn:agency-active", "Sub-Agent")
    return {
        "agencies": (
            "stage_agencies",
            [
                {
                    "agency_tdi_id": "npn:agency-new",
                    "agency_npn": "agency-new",
                    "agency_ein": None,
                    "name": "New Market Insurance LLC",
                    "agency_type": "Corporation",
                    "license_type": "Property and Casualty Agency",
                    "qualification": "General Lines",
                    "license_issue_date": date.today(),
                    "expiration_date": None,
                    "city": "Austin",
                    "state": "TX",
                    "postal_code": "78701",
                    "county": "Travis",
                }
            ],
        ),
        "relationships": (
            "stage_agent_agency_links",
            [
                {
                    "agent_npn": "9003",
                    "agent_name": "Active Producer",
                    "agency_tdi_id": "npn:agency-active",
                    "agency_ein": None,
                    "agency_name": "Still Active Agency",
                    "association_type": "Sub-Agent",
                    "relationship_started_at": date(2020, 1, 1),
                    "confidence": "high",
                    "structural_hash": active_hash,
                }
            ],
        ),
        "agency_appointments": ("stage_agency_appointments", []),
        "agent_appointments": ("stage_agent_appointments", []),
    }


def main() -> None:
    load_dotenv()
    settings = get_settings()
    if not settings.database_url:
        raise SystemExit("DATABASE_URL is required.")

    with connect(settings.database_url) as conn:
        conn.execute(
            """
            INSERT INTO master_agencies (agency_tdi_id, name, physical_zip, county, first_seen_date)
            VALUES
              ('npn:agency-old', 'Old Agency', '75001', 'Dallas', CURRENT_DATE - INTERVAL '3 years'),
              ('npn:agency-short', 'Short Tenure Agency', '77001', 'Harris', CURRENT_DATE - INTERVAL '1 year'),
              ('npn:agency-active', 'Still Active Agency', '78701', 'Travis', CURRENT_DATE - INTERVAL '4 years')
            ON CONFLICT (agency_tdi_id) DO NOTHING
            """
        )
        conn.execute(
            """
            INSERT INTO master_agents (agent_npn, full_name)
            VALUES ('9001', 'Long Tenure Producer'), ('9002', 'Short Tenure Producer'), ('9003', 'Active Producer')
            ON CONFLICT (agent_npn) DO NOTHING
            """
        )
        conn.execute(
            """
            INSERT INTO master_agent_agency_links (
              agent_npn, agency_tdi_id, association_type, relationship_started_at,
              first_seen_date, last_seen_date, structural_hash, is_active, confidence
            )
            VALUES
              ('9001', 'npn:agency-old', 'Sub-Agent', CURRENT_DATE - INTERVAL '25 months', CURRENT_DATE - INTERVAL '25 months', CURRENT_DATE, %s, TRUE, 'high'),
              ('9002', 'npn:agency-short', 'Sub-Agent', CURRENT_DATE - INTERVAL '23 months', CURRENT_DATE - INTERVAL '23 months', CURRENT_DATE, %s, TRUE, 'high'),
              ('9003', 'npn:agency-active', 'Sub-Agent', CURRENT_DATE - INTERVAL '4 years', CURRENT_DATE - INTERVAL '4 years', CURRENT_DATE, %s, TRUE, 'high')
            ON CONFLICT (agent_npn, agency_tdi_id, association_type) DO NOTHING
            """,
            (
                structural_hash("9001", "npn:agency-old", "Sub-Agent"),
                structural_hash("9002", "npn:agency-short", "Sub-Agent"),
                structural_hash("9003", "npn:agency-active", "Sub-Agent"),
            ),
        )
        reset_staging_and_load(conn, fixture_rows())
        generate_events_sql(conn)
        conn.commit()
    print("Seeded Insuretra fixture rows and generated fixture events.")


if __name__ == "__main__":
    main()

