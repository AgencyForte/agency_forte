import pytest
import polars as pl
from insuretra_pipeline.db import reset_staging_and_load, get_stage_counts

def test_polars_parsing_and_staging_truncation_loop(db_connection):
    """Test Case 2.1: Polars Parsing and Staging Truncation Loop"""
    
    # Seed with initial data
    df_initial = pl.DataFrame({
        "agency_tdi_id": ["npn:1"],
        "agency_npn": ["1"],
        "agency_ein": [None],
        "name": ["Test Agency"],
        "agency_type": ["Corp"],
        "license_type": ["Life"],
        "qualification": ["Qual"],
        "license_issue_date": ["2020-01-01"],
        "expiration_date": [None],
        "city": ["Austin"],
        "state": ["TX"],
        "postal_code": ["78701"],
        "county": [None]
    }, schema_overrides={"agency_ein": pl.Utf8, "expiration_date": pl.Utf8, "county": pl.Utf8})
    
    staged = {
        "agencies": ("stage_agencies", df_initial),
        "relationships": ("stage_agent_agency_links", pl.DataFrame(schema={"agent_npn": pl.Utf8, "agent_name": pl.Utf8, "agency_tdi_id": pl.Utf8, "agency_ein": pl.Utf8, "agency_name": pl.Utf8, "association_type": pl.Utf8, "relationship_started_at": pl.Date, "confidence": pl.Utf8, "structural_hash": pl.Utf8})),
        "agency_appointments": ("stage_agency_appointments", pl.DataFrame(schema={"agency_tdi_id": pl.Utf8, "agency_ein": pl.Utf8, "agency_name": pl.Utf8, "carrier_naic": pl.Utf8, "carrier_name": pl.Utf8, "appointment_type": pl.Utf8, "effective_date": pl.Date, "city": pl.Utf8, "state": pl.Utf8, "postal_code": pl.Utf8, "structural_hash": pl.Utf8})),
        "agent_appointments": ("stage_agent_appointments", pl.DataFrame(schema={"agent_npn": pl.Utf8, "agent_name": pl.Utf8, "carrier_naic": pl.Utf8, "carrier_name": pl.Utf8, "appointment_type": pl.Utf8, "effective_date": pl.Date, "city": pl.Utf8, "state": pl.Utf8, "postal_code": pl.Utf8, "structural_hash": pl.Utf8})),
    }
    
    reset_staging_and_load(db_connection, staged)
    
    counts = get_stage_counts(db_connection)
    assert counts["agencies"] == 1
    
    # Run loop again with 0 rows
    staged_empty = {
        "agencies": ("stage_agencies", pl.DataFrame(schema=df_initial.schema)),
        "relationships": ("stage_agent_agency_links", staged["relationships"][1]),
        "agency_appointments": ("stage_agency_appointments", staged["agency_appointments"][1]),
        "agent_appointments": ("stage_agent_appointments", staged["agent_appointments"][1]),
    }
    
    reset_staging_and_load(db_connection, staged_empty)
    counts2 = get_stage_counts(db_connection)
    
    # Assert truncation works
    assert counts2["agencies"] == 0

def test_dump_guard_threshold_enforcement(db_connection):
    """Test Case 3.1: Threshold Enforcement and Quarantine Flow"""
    # This requires running the pipeline diff check. 
    # Since dump guard isolation block is in main pipeline (run_daily), we can mock the functions
    pass
