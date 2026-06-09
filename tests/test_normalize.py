from datetime import date

from insuretra_pipeline.hashing import structural_hash
from insuretra_pipeline.normalize import (
    normalize_agency,
    normalize_agency_appointment,
    normalize_agent_appointment,
    normalize_relationship,
    normalize_zip,
)


def test_normalize_zip_keeps_first_five_digits():
    assert normalize_zip("103071229") == "10307"
    assert normalize_zip("TX 78701-1234") == "78701"
    assert normalize_zip("abc") is None


def test_normalize_agency_master_row():
    row = normalize_agency(
        {
            "npn": "10003569",
            "agency_license_number": "2282655",
            "org_name": " CHELSEA MORGAN SECURITIES INC ",
            "agency_type": "Corporation",
            "license_type": "Life Agency",
            "qualification": "Life Agent/Agency",
            "license_issue_date": "2018-03-22T00:00:00.000",
            "expiration_date": "2028-03-22T00:00:00.000",
            "city": "STATEN ISLAND",
            "state": "NY",
            "pstl_cd": "103071229",
        }
    )

    assert row["agency_tdi_id"] == "npn:10003569"
    assert row["name"] == "CHELSEA MORGAN SECURITIES INC"
    assert row["postal_code"] == "10307"
    assert row["license_issue_date"] == date(2018, 3, 22)


def test_normalize_relationship_builds_sub_agent_hash():
    row = normalize_relationship(
        {
            "associated_licensee_name": "Producer One",
            "associated_licensee_npn": "9001",
            "association_type": "Sub-Agent",
            "licensee_name": "Agency One",
            "licensee_npn": "12345",
            "licensee_ein": "111222333",
            "association_begin_date": "2020-01-15T00:00:00.000",
        }
    )

    assert row["agent_npn"] == "9001"
    assert row["agency_tdi_id"] == "npn:12345"
    assert row["structural_hash"] == structural_hash("9001", "npn:12345", "Sub-Agent")
    assert row["relationship_started_at"] == date(2020, 1, 15)


def test_normalize_appointments_cover_agent_and_agency_sources():
    agency = normalize_agency_appointment(
        {
            "naic_id": "51624",
            "company": "First American Title Guaranty Company",
            "active_date": "2026-03-06T00:00:00.000",
            "appointment_type": "Underwriter",
            "npn": "22142794",
            "ein": "413016274",
            "agency_name": "HAVEN NATIONAL TITLE GROUP, LLC",
            "zip": "79765",
        }
    )
    agent = normalize_agent_appointment(
        {
            "naic_id": "95490",
            "company": "Aetna Health Inc.",
            "active_date": "2016-08-29T00:00:00.000",
            "appointment_type": "Life, Accident, Health and HMO",
            "npn_ein": "16185407",
            "licensee": "ISSAC MIRANDA",
            "postal_cd": "78572",
        }
    )

    assert agency["agency_tdi_id"] == "npn:22142794"
    assert agency["carrier_naic"] == "51624"
    assert agent["agent_npn"] == "16185407"
    assert agent["postal_code"] == "78572"

