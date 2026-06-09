from __future__ import annotations

from datetime import date, datetime
import re
from typing import Any

from .hashing import structural_hash


def blank_to_none(value: Any) -> Any:
    if value is None:
        return None
    if isinstance(value, str):
        stripped = value.strip()
        return stripped if stripped else None
    return value


def normalize_zip(value: Any) -> str | None:
    value = blank_to_none(value)
    if value is None:
        return None
    digits = re.sub(r"\D", "", str(value))
    if len(digits) < 5:
        return None
    return digits[:5]


def normalize_text(value: Any) -> str | None:
    value = blank_to_none(value)
    if value is None:
        return None
    return re.sub(r"\s+", " ", str(value)).strip()


def parse_date(value: Any) -> date | None:
    value = blank_to_none(value)
    if value is None:
        return None
    if isinstance(value, date) and not isinstance(value, datetime):
        return value
    text = str(value).strip()
    for fmt in ("%Y-%m-%dT%H:%M:%S.%f", "%Y-%m-%dT%H:%M:%S", "%Y-%m-%d"):
        try:
            return datetime.strptime(text, fmt).date()
        except ValueError:
            continue
    return None


def agency_id_from_npn_or_license(npn: Any, license_number: Any = None) -> str | None:
    npn = normalize_text(npn)
    license_number = normalize_text(license_number)
    if npn:
        return f"npn:{npn}"
    if license_number:
        return f"lic:{license_number}"
    return None


def normalize_agency(row: dict[str, Any]) -> dict[str, Any]:
    return {
        "agency_tdi_id": agency_id_from_npn_or_license(row.get("npn"), row.get("agency_license_number")),
        "agency_npn": normalize_text(row.get("npn")),
        "agency_ein": None,
        "name": normalize_text(row.get("org_name")),
        "agency_type": normalize_text(row.get("agency_type")),
        "license_type": normalize_text(row.get("license_type")),
        "qualification": normalize_text(row.get("qualification")),
        "license_issue_date": parse_date(row.get("license_issue_date")),
        "expiration_date": parse_date(row.get("expiration_date")),
        "city": normalize_text(row.get("city")),
        "state": normalize_text(row.get("state")),
        "postal_code": normalize_zip(row.get("pstl_cd")),
        "county": normalize_text(row.get("county")),
    }


def normalize_relationship(row: dict[str, Any]) -> dict[str, Any]:
    agent_npn = normalize_text(row.get("associated_licensee_npn"))
    agency_tdi_id = agency_id_from_npn_or_license(row.get("licensee_npn"), None)
    association_type = normalize_text(row.get("association_type"))
    started_at = parse_date(row.get("association_begin_date"))
    row_out = {
        "agent_npn": agent_npn,
        "agent_name": normalize_text(row.get("associated_licensee_name")),
        "agency_tdi_id": agency_tdi_id,
        "agency_ein": normalize_text(row.get("licensee_ein")),
        "agency_name": normalize_text(row.get("licensee_name")),
        "association_type": association_type,
        "relationship_started_at": started_at,
        "confidence": "high" if started_at else "lower_first_seen_fallback",
    }
    row_out["structural_hash"] = structural_hash(agent_npn, agency_tdi_id, association_type)
    return row_out


def normalize_agency_appointment(row: dict[str, Any]) -> dict[str, Any]:
    agency_tdi_id = agency_id_from_npn_or_license(row.get("npn"), None)
    carrier_naic = normalize_text(row.get("naic_id"))
    appointment_type = normalize_text(row.get("appointment_type"))
    row_out = {
        "agency_tdi_id": agency_tdi_id,
        "agency_ein": normalize_text(row.get("ein")),
        "agency_name": normalize_text(row.get("agency_name")),
        "carrier_naic": carrier_naic,
        "carrier_name": normalize_text(row.get("company")),
        "appointment_type": appointment_type,
        "effective_date": parse_date(row.get("active_date")),
        "city": normalize_text(row.get("city")),
        "state": normalize_text(row.get("state")),
        "postal_code": normalize_zip(row.get("zip")),
    }
    row_out["structural_hash"] = structural_hash(agency_tdi_id, carrier_naic, appointment_type)
    return row_out


def normalize_agent_appointment(row: dict[str, Any]) -> dict[str, Any]:
    agent_npn = normalize_text(row.get("npn_ein"))
    carrier_naic = normalize_text(row.get("naic_id"))
    appointment_type = normalize_text(row.get("appointment_type"))
    row_out = {
        "agent_npn": agent_npn,
        "agent_name": normalize_text(row.get("licensee")),
        "carrier_naic": carrier_naic,
        "carrier_name": normalize_text(row.get("company")),
        "appointment_type": appointment_type,
        "effective_date": parse_date(row.get("active_date")),
        "city": normalize_text(row.get("city")),
        "state": normalize_text(row.get("state")),
        "postal_code": normalize_zip(row.get("postal_cd")),
    }
    row_out["structural_hash"] = structural_hash(agent_npn, carrier_naic, appointment_type)
    return row_out


NORMALIZERS = {
    "agencies": normalize_agency,
    "relationships": normalize_relationship,
    "agency_appointments": normalize_agency_appointment,
    "agent_appointments": normalize_agent_appointment,
}


def normalize_rows(dataset_key: str, rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    normalizer = NORMALIZERS[dataset_key]
    return [row for row in (normalizer(raw) for raw in rows) if all_required_present(dataset_key, row)]


def all_required_present(dataset_key: str, row: dict[str, Any]) -> bool:
    required = {
        "agencies": ("agency_tdi_id", "name"),
        "relationships": ("agent_npn", "agency_tdi_id", "association_type", "structural_hash"),
        "agency_appointments": ("agency_tdi_id", "carrier_naic", "carrier_name", "structural_hash"),
        "agent_appointments": ("agent_npn", "carrier_naic", "carrier_name", "structural_hash"),
    }[dataset_key]
    return all(row.get(key) for key in required)

