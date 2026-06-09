import polars as pl
from datetime import date

from insuretra_pipeline.normalize import (
    normalize_agency,
    normalize_agency_appointment,
    normalize_agent_appointment,
    normalize_relationship,
    normalize_zip,
)


def test_normalize_zip_keeps_first_five_digits():
    df = pl.DataFrame({"Postal code": ["103071229", "TX 78701-1234", "abc", None]})
    res = df.select(normalize_zip(pl.col("Postal code")).alias("norm"))["norm"].to_list()
    assert res == ["10307", "78701", None, None]


def test_normalize_agency_master_row():
    df = pl.DataFrame({
        "NPN": ["10003569"],
        "License number": ["2282655"],
        "Name": [" CHELSEA MORGAN SECURITIES INC "],
        "Org type": ["Corporation"],
        "License type": ["Life Agency"],
        "Qualification": ["Life Agent/Agency"],
        "Issue date": ["2018-03-22T00:00:00.000"],
        "Expiration date": ["2028-03-22T00:00:00.000"],
        "City": ["STATEN ISLAND"],
        "State": ["NY"],
        "Postal code": ["103071229"],
        "County (if title agency)": [None]
    })
    
    out = normalize_agency(df).to_dicts()[0]
    assert out["agency_tdi_id"] == "npn:10003569"
    assert out["name"] == "CHELSEA MORGAN SECURITIES INC"
    assert out["postal_code"] == "10307"
    assert out["license_issue_date"] == date(2018, 3, 22)


def test_normalize_relationship_builds_sub_agent_hash():
    df = pl.DataFrame({
        "Associated licensee name": ["Producer One"],
        "Associated licensee NPN": ["9001"],
        "Association type": ["Sub-Agent"],
        "Licensee name": ["Agency One"],
        "Licensee NPN": ["12345"],
        "Licensee EIN": ["111222333"],
        "Association begin date": ["2020-01-15T00:00:00.000"],
    })
    out = normalize_relationship(df).to_dicts()[0]
    assert out["agent_npn"] == "9001"
    assert out["agency_tdi_id"] == "npn:12345"
    assert out["relationship_started_at"] == date(2020, 1, 15)


def test_normalize_appointments_cover_agent_and_agency_sources():
    agency_df = pl.DataFrame({
        "NAIC ID": ["51624"],
        "Insurance company name": ["First American Title Guaranty Company"],
        "Appointment active date": ["2026-03-06T00:00:00.000"],
        "Appointment type": ["Underwriter"],
        "Agency NPN": ["22142794"],
        "Agency EIN": ["413016274"],
        "Agency name": ["HAVEN NATIONAL TITLE GROUP, LLC"],
        "Postal code": ["79765"],
        "City": [None],
        "State": [None],
    })
    agent_df = pl.DataFrame({
        "NAIC ID": ["95490"],
        "Insurance company name": ["Aetna Health Inc."],
        "Appointment active date": ["2016-08-29T00:00:00.000"],
        "Appointment type": ["Life, Accident, Health and HMO"],
        "Agent NPN": ["16185407"],
        "Agent name": ["ISSAC MIRANDA"],
        "Postal code": ["78572"],
        "City": [None],
        "State": [None],
    })
    
    agency = normalize_agency_appointment(agency_df).to_dicts()[0]
    agent = normalize_agent_appointment(agent_df).to_dicts()[0]

    assert agency["agency_tdi_id"] == "npn:22142794"
    assert agency["carrier_naic"] == "51624"
    assert agent["agent_npn"] == "16185407"
    assert agent["postal_code"] == "78572"
