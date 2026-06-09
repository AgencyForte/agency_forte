from __future__ import annotations

from contextlib import contextmanager
from datetime import date
import io
import json
from typing import Any, Iterable

import polars as pl
import psycopg
from psycopg.rows import dict_row


@contextmanager
def connect(database_url: str):
    with psycopg.connect(database_url, row_factory=dict_row) as conn:
        yield conn


def create_pipeline_run(conn) -> str:
    row = conn.execute("INSERT INTO pipeline_runs DEFAULT VALUES RETURNING run_id").fetchone()
    conn.commit()
    return str(row["run_id"])


def finish_pipeline_run(conn, run_id: str, status: str, row_delta: int | None, message: str | None = None) -> None:
    conn.execute(
        """
        UPDATE pipeline_runs
        SET finished_at = NOW(),
            status = %s,
            row_delta = COALESCE(%s, row_delta),
            message = COALESCE(%s, message),
            event_count = (SELECT COUNT(*) FROM market_timeline WHERE detected_at >= pipeline_runs.started_at),
            suppressed_count = (SELECT COUNT(*) FROM suppressed_severances WHERE detected_at >= pipeline_runs.started_at)
        WHERE run_id = %s
        """,
        (status, row_delta, message, run_id),
    )
    conn.commit()


def log(conn, run_id: str | None, level: str, message: str, metadata: dict[str, Any] | None = None) -> None:
    conn.execute(
        "INSERT INTO pipeline_logs (run_id, level, message, metadata) VALUES (%s, %s, %s, %s)",
        (run_id, level, message, json.dumps(metadata or {})),
    )


def anomaly(conn, run_id: str | None, anomaly_type: str, message: str, severity: str = "warning", metadata: dict | None = None) -> None:
    conn.execute(
        """
        INSERT INTO pipeline_anomalies (run_id, anomaly_type, severity, message, metadata)
        VALUES (%s, %s, %s, %s, %s)
        """,
        (run_id, anomaly_type, severity, message, json.dumps(metadata or {})),
    )


def truncate_staging(conn, tables: Iterable[str]) -> None:
    for table in tables:
        conn.execute(f"TRUNCATE TABLE {table}")


def insert_rows(conn, table: str, df: pl.DataFrame) -> None:
    if df.is_empty():
        return
    buffer = io.BytesIO()
    df.write_csv(buffer)
    buffer.seek(0)
    with conn.cursor() as cur:
        with cur.copy(f"COPY {table} FROM STDIN WITH CSV HEADER") as copy:
            copy.write(buffer.read())


def get_stage_counts(conn) -> dict[str, int]:
    tables = {
        "agencies": "stage_agencies",
        "links": "stage_agent_agency_links",
        "agency_appointments": "stage_agency_appointments",
        "agent_appointments": "stage_agent_appointments",
    }
    return {key: conn.execute(f"SELECT COUNT(*) AS count FROM {table}").fetchone()["count"] for key, table in tables.items()}


def get_master_counts(conn) -> dict[str, int]:
    return {
        "agencies": conn.execute("SELECT COUNT(*) AS count FROM master_agencies").fetchone()["count"],
        "links": conn.execute("SELECT COUNT(*) AS count FROM master_agent_agency_links WHERE is_active").fetchone()["count"],
        "agency_appointments": conn.execute("SELECT COUNT(*) AS count FROM master_agency_appointments WHERE is_active").fetchone()["count"],
        "agent_appointments": conn.execute("SELECT COUNT(*) AS count FROM master_agent_appointments WHERE is_active").fetchone()["count"],
    }


def generate_events_sql(conn) -> None:
    conn.execute(
        """
        INSERT INTO suppressed_severances (
          agent_npn, agency_tdi_id, association_type, relationship_started_at,
          relationship_ended_at, tenure_months, suppression_reason, structural_hash, payload
        )
        SELECT
          m.agent_npn,
          m.agency_tdi_id,
          m.association_type,
          COALESCE(m.relationship_started_at, m.first_seen_date),
          CURRENT_DATE,
          CASE
            WHEN COALESCE(m.relationship_started_at, m.first_seen_date) IS NULL THEN NULL
            ELSE (
              DATE_PART('year', AGE(CURRENT_DATE, COALESCE(m.relationship_started_at, m.first_seen_date))) * 12
              + DATE_PART('month', AGE(CURRENT_DATE, COALESCE(m.relationship_started_at, m.first_seen_date)))
            )::INT
          END,
          'TENURE_UNDER_36_MONTHS',
          m.structural_hash,
          jsonb_build_object('source_rule', '36_month_tenure_filter', 'association_type', m.association_type)
        FROM master_agent_agency_links m
        LEFT JOIN stage_agent_agency_links s ON s.structural_hash = m.structural_hash
        WHERE m.is_active
          AND LOWER(m.association_type) = 'sub-agent'
          AND s.structural_hash IS NULL
          AND (
            COALESCE(m.relationship_started_at, m.first_seen_date) IS NULL
            OR (
              DATE_PART('year', AGE(CURRENT_DATE, COALESCE(m.relationship_started_at, m.first_seen_date))) * 12
              + DATE_PART('month', AGE(CURRENT_DATE, COALESCE(m.relationship_started_at, m.first_seen_date)))
            ) < 36
          )
        ON CONFLICT (structural_hash, relationship_ended_at) DO NOTHING
        """
    )
    conn.execute(
        """
        INSERT INTO market_timeline (
          event_type, target_agency_id, target_agent_npn, event_zip, event_county,
          confidence, event_fingerprint, payload
        )
        SELECT
          'COMPETITOR_BLEEDING',
          m.agency_tdi_id,
          m.agent_npn,
          a.physical_zip,
          a.county,
          m.confidence,
          encode(digest('COMPETITOR_BLEEDING|' || m.agent_npn || '|' || m.agency_tdi_id || '|' || CURRENT_DATE::TEXT, 'sha256'), 'hex'),
          jsonb_build_object(
            'source_rule', '36_month_tenure_filter', 
            'association_type', m.association_type,
            'departing_carriers', COALESCE(carriers.carrier_list, '[]'::jsonb)
          )
        FROM master_agent_agency_links m
        LEFT JOIN stage_agent_agency_links s ON s.structural_hash = m.structural_hash
        LEFT JOIN master_agencies a ON a.agency_tdi_id = m.agency_tdi_id
        LEFT JOIN LATERAL (
          SELECT jsonb_agg(jsonb_build_object('carrier_naic', map.carrier_naic, 'carrier_name', map.carrier_name)) AS carrier_list
          FROM master_agent_appointments map
          WHERE map.agent_npn = m.agent_npn AND map.is_active
        ) carriers ON TRUE
        WHERE m.is_active
          AND LOWER(m.association_type) = 'sub-agent'
          AND s.structural_hash IS NULL
          AND (
            DATE_PART('year', AGE(CURRENT_DATE, COALESCE(m.relationship_started_at, m.first_seen_date))) * 12
            + DATE_PART('month', AGE(CURRENT_DATE, COALESCE(m.relationship_started_at, m.first_seen_date)))
          ) >= 36
        ON CONFLICT (event_fingerprint) DO NOTHING
        """
    )
    conn.execute(
        """
        INSERT INTO market_timeline (
          event_type, target_agency_id, carrier_naic, carrier_name, event_zip, event_county,
          confidence, event_fingerprint, payload
        )
        SELECT
          'COMPETITOR_BLEEDING',
          m.agency_tdi_id,
          m.carrier_naic,
          m.carrier_name,
          a.physical_zip,
          a.county,
          'high',
          encode(digest('COMPETITOR_BLEEDING_CARRIER|' || m.agency_tdi_id || '|' || m.carrier_naic || '|' || COALESCE(m.appointment_type, '') || '|' || CURRENT_DATE::TEXT, 'sha256'), 'hex'),
          jsonb_build_object(
            'source_rule', 'agency_lost_carrier',
            'appointment_type', m.appointment_type,
            'effective_date', m.effective_date
          )
        FROM master_agency_appointments m
        LEFT JOIN stage_agency_appointments s ON s.structural_hash = m.structural_hash
        LEFT JOIN master_agencies a ON a.agency_tdi_id = m.agency_tdi_id
        WHERE m.is_active
          AND s.structural_hash IS NULL
          AND (
            DATE_PART('year', AGE(CURRENT_DATE, COALESCE(m.effective_date, m.first_seen_date))) * 12
            + DATE_PART('month', AGE(CURRENT_DATE, COALESCE(m.effective_date, m.first_seen_date)))
          ) >= 24
        ON CONFLICT (event_fingerprint) DO NOTHING
        """
    )
    conn.execute(
        """
        INSERT INTO market_timeline (
          event_type, target_agency_id, carrier_naic, carrier_name, event_zip, event_county,
          confidence, event_fingerprint, payload
        )
        SELECT
          'CARRIER_LAND_GRAB',
          s.agency_tdi_id,
          s.carrier_naic,
          s.carrier_name,
          a.physical_zip,
          a.county,
          'high',
          encode(digest('CARRIER_LAND_GRAB|' || s.agency_tdi_id || '|' || s.carrier_naic || '|' || COALESCE(s.appointment_type, ''), 'sha256'), 'hex'),
          jsonb_build_object('appointment_type', s.appointment_type, 'effective_date', s.effective_date, 'line_of_business', cm.line_of_business)
        FROM stage_agency_appointments s
        JOIN master_agencies a ON a.agency_tdi_id = s.agency_tdi_id
        LEFT JOIN master_agency_appointments m ON m.structural_hash = s.structural_hash
        LEFT JOIN carrier_to_line_matrix cm ON cm.carrier_naic = s.carrier_naic
        WHERE m.structural_hash IS NULL
          AND a.first_seen_date <= CURRENT_DATE - INTERVAL '30 days'
        ON CONFLICT (event_fingerprint) DO NOTHING
        """
    )
    conn.execute(
        """
        INSERT INTO market_timeline (
          event_type, target_agency_id, event_zip, event_county, confidence, event_fingerprint, payload
        )
        WITH new_agencies AS (
          SELECT s.*
          FROM stage_agencies s
          LEFT JOIN master_agencies m ON m.agency_tdi_id = s.agency_tdi_id
          WHERE m.agency_tdi_id IS NULL
        ),
        inserted AS (
          INSERT INTO master_agencies (
            agency_tdi_id, agency_npn, agency_ein, name, physical_city, physical_state, physical_zip, county
          )
          SELECT agency_tdi_id, agency_npn, agency_ein, name, city, state, postal_code, county
          FROM new_agencies
          ON CONFLICT (agency_tdi_id) DO NOTHING
          RETURNING agency_tdi_id, name, physical_zip, county
        )
        SELECT
          'NEW_MARKET_ENTRY',
          i.agency_tdi_id,
          i.physical_zip,
          i.county,
          'high',
          encode(digest('NEW_MARKET_ENTRY|' || i.agency_tdi_id, 'sha256'), 'hex'),
          jsonb_build_object('agency_name', i.name)
        FROM inserted i
        ON CONFLICT (event_fingerprint) DO NOTHING
        """
    )
    conn.execute(
        """
        INSERT INTO market_timeline (
          event_type, target_agency_id, target_agent_npn, event_zip, event_county, confidence, event_fingerprint, payload
        )
        SELECT
          'LOB_ENCROACHMENT',
          l.agency_tdi_id,
          l.agent_npn,
          a.physical_zip,
          a.county,
          'high',
          encode(digest('LOB_ENCROACHMENT|' || l.agent_npn || '|' || l.agency_tdi_id || '|' || CURRENT_DATE::TEXT, 'sha256'), 'hex'),
          jsonb_build_object('source_rule', 'veteran_hire_overlap', 'lines_overlapped', overlapping.lines, 'historical_carriers', overlapping.historical_carriers)
        FROM stage_agent_agency_links l
        LEFT JOIN master_agent_agency_links m ON m.structural_hash = l.structural_hash
        JOIN master_agents ma ON ma.agent_npn = l.agent_npn
        JOIN master_agencies a ON a.agency_tdi_id = l.agency_tdi_id
        JOIN (
          SELECT agent_npn, 
                 array_agg(DISTINCT cm.line_of_business) AS lines,
                 jsonb_agg(DISTINCT jsonb_build_object('carrier_naic', map.carrier_naic, 'carrier_name', map.carrier_name)) AS historical_carriers
          FROM master_agent_appointments map
          JOIN carrier_to_line_matrix cm ON cm.carrier_naic = map.carrier_naic
          WHERE map.is_active
          GROUP BY agent_npn
        ) overlapping ON overlapping.agent_npn = l.agent_npn
        WHERE m.structural_hash IS NULL
          AND LOWER(l.association_type) = 'sub-agent'
          AND (
            DATE_PART('year', AGE(CURRENT_DATE, ma.first_seen_date)) * 12
            + DATE_PART('month', AGE(CURRENT_DATE, ma.first_seen_date))
          ) >= 36
        ON CONFLICT (event_fingerprint) DO NOTHING
        """
    )


def process_events_geo(conn) -> None:
    conn.execute(
        """
        WITH geo_matched AS (
          SELECT m.event_id, z.centroid, z.geometry
          FROM market_timeline m
          JOIN texas_zip_geo z ON z.zip = m.event_zip
          WHERE NOT m.is_processed AND m.event_zip IS NOT NULL
        )
        UPDATE market_timeline m
        SET is_processed = TRUE,
            payload = jsonb_set(
              m.payload, 
              '{geo_routing}', 
              jsonb_build_object('processed', true, 'zip', m.event_zip)
            )
        FROM geo_matched g
        WHERE m.event_id = g.event_id;
        """
    )


def consolidate_master_sql(conn) -> None:
    conn.execute(
        """
        INSERT INTO master_agencies (
          agency_tdi_id, agency_npn, agency_ein, name, physical_city, physical_state, physical_zip, county
        )
        SELECT DISTINCT agency_tdi_id, agency_npn, agency_ein, name, city, state, postal_code, county
        FROM stage_agencies
        ON CONFLICT (agency_tdi_id) DO UPDATE SET
          agency_npn = COALESCE(EXCLUDED.agency_npn, master_agencies.agency_npn),
          agency_ein = COALESCE(EXCLUDED.agency_ein, master_agencies.agency_ein),
          name = EXCLUDED.name,
          physical_city = COALESCE(EXCLUDED.physical_city, master_agencies.physical_city),
          physical_state = COALESCE(EXCLUDED.physical_state, master_agencies.physical_state),
          physical_zip = COALESCE(EXCLUDED.physical_zip, master_agencies.physical_zip),
          county = COALESCE(EXCLUDED.county, master_agencies.county),
          updated_at = NOW()
        """
    )
    conn.execute(
        """
        INSERT INTO master_agencies (agency_tdi_id, agency_ein, name, physical_city, physical_state, physical_zip)
        SELECT DISTINCT agency_tdi_id, agency_ein, agency_name, city, state, postal_code
        FROM stage_agency_appointments
        WHERE agency_tdi_id NOT IN (SELECT agency_tdi_id FROM master_agencies)
        ON CONFLICT (agency_tdi_id) DO NOTHING
        """
    )
    conn.execute(
        """
        INSERT INTO master_agencies (agency_tdi_id, agency_ein, name)
        SELECT DISTINCT agency_tdi_id, agency_ein, agency_name
        FROM stage_agent_agency_links
        WHERE agency_tdi_id NOT IN (SELECT agency_tdi_id FROM master_agencies)
        ON CONFLICT (agency_tdi_id) DO NOTHING
        """
    )
    conn.execute(
        """
        INSERT INTO master_agents (agent_npn, full_name, city, state, postal_code)
        SELECT DISTINCT agent_npn, agent_name, city, state, postal_code
        FROM stage_agent_appointments
        ON CONFLICT (agent_npn) DO UPDATE SET
          full_name = EXCLUDED.full_name,
          city = COALESCE(EXCLUDED.city, master_agents.city),
          state = COALESCE(EXCLUDED.state, master_agents.state),
          postal_code = COALESCE(EXCLUDED.postal_code, master_agents.postal_code),
          updated_at = NOW()
        """
    )
    conn.execute(
        """
        INSERT INTO master_agents (agent_npn, full_name)
        SELECT DISTINCT agent_npn, agent_name
        FROM stage_agent_agency_links
        ON CONFLICT (agent_npn) DO UPDATE SET
          full_name = COALESCE(EXCLUDED.full_name, master_agents.full_name),
          updated_at = NOW()
        """
    )
    conn.execute(
        """
        UPDATE master_agent_agency_links m
        SET is_active = FALSE, last_seen_date = CURRENT_DATE, updated_at = NOW()
        WHERE is_active
          AND NOT EXISTS (SELECT 1 FROM stage_agent_agency_links s WHERE s.structural_hash = m.structural_hash)
        """
    )
    conn.execute(
        """
        INSERT INTO master_agent_agency_links (
          agent_npn, agency_tdi_id, agency_ein, association_type, relationship_started_at,
          first_seen_date, last_seen_date, structural_hash, is_active, confidence
        )
        SELECT agent_npn, agency_tdi_id, agency_ein, association_type, relationship_started_at,
               CURRENT_DATE, CURRENT_DATE, structural_hash, TRUE, confidence
        FROM stage_agent_agency_links
        ON CONFLICT (agent_npn, agency_tdi_id, association_type) DO UPDATE SET
          agency_ein = COALESCE(EXCLUDED.agency_ein, master_agent_agency_links.agency_ein),
          relationship_started_at = COALESCE(EXCLUDED.relationship_started_at, master_agent_agency_links.relationship_started_at),
          last_seen_date = CURRENT_DATE,
          structural_hash = EXCLUDED.structural_hash,
          is_active = TRUE,
          confidence = EXCLUDED.confidence,
          updated_at = NOW()
        """
    )
    conn.execute(
        """
        UPDATE master_agency_appointments m
        SET is_active = FALSE, last_seen_date = CURRENT_DATE, updated_at = NOW()
        WHERE is_active
          AND NOT EXISTS (SELECT 1 FROM stage_agency_appointments s WHERE s.structural_hash = m.structural_hash)
        """
    )
    conn.execute(
        """
        INSERT INTO master_agency_appointments (
          agency_tdi_id, agency_ein, carrier_naic, carrier_name, appointment_type,
          effective_date, first_seen_date, last_seen_date, structural_hash, is_active
        )
        SELECT agency_tdi_id, agency_ein, carrier_naic, carrier_name, appointment_type,
               effective_date, CURRENT_DATE, CURRENT_DATE, structural_hash, TRUE
        FROM stage_agency_appointments
        ON CONFLICT (agency_tdi_id, carrier_naic, appointment_type) DO UPDATE SET
          carrier_name = EXCLUDED.carrier_name,
          effective_date = COALESCE(EXCLUDED.effective_date, master_agency_appointments.effective_date),
          last_seen_date = CURRENT_DATE,
          structural_hash = EXCLUDED.structural_hash,
          is_active = TRUE,
          updated_at = NOW()
        """
    )
    conn.execute(
        """
        UPDATE master_agent_appointments m
        SET is_active = FALSE, last_seen_date = CURRENT_DATE, updated_at = NOW()
        WHERE is_active
          AND NOT EXISTS (SELECT 1 FROM stage_agent_appointments s WHERE s.structural_hash = m.structural_hash)
        """
    )
    conn.execute(
        """
        INSERT INTO master_agent_appointments (
          agent_npn, carrier_naic, carrier_name, appointment_type,
          effective_date, first_seen_date, last_seen_date, structural_hash, is_active
        )
        SELECT agent_npn, carrier_naic, carrier_name, appointment_type,
               effective_date, CURRENT_DATE, CURRENT_DATE, structural_hash, TRUE
        FROM stage_agent_appointments
        ON CONFLICT (agent_npn, carrier_naic, appointment_type) DO UPDATE SET
          carrier_name = EXCLUDED.carrier_name,
          effective_date = COALESCE(EXCLUDED.effective_date, master_agent_appointments.effective_date),
          last_seen_date = CURRENT_DATE,
          structural_hash = EXCLUDED.structural_hash,
          is_active = TRUE,
          updated_at = NOW()
        """
    )


def reset_staging_and_load(conn, staged: dict[str, tuple[str, pl.DataFrame]]) -> None:
    truncate_staging(conn, [table for table, _ in staged.values()])
    for table, df in staged.values():
        insert_rows(conn, table, df)
    conn.commit()
